# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2010 TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#
import os
from string import letters
from multiprocessing import Process, Queue  # , cpu_count
import subprocess
from Queue import Empty

try:
    from PyQt5.QtCore import QCoreApplication
    _ = QCoreApplication.translate
except Exception:
    _ = lambda x, y: y

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QTimer, QMutex, QWaitCondition  # pyqtSignal, QObject
from PyQt5.QtGui import QPixmap

import pisi.ui

import yali.util
import yali.pisiiface
import yali.postinstall
import yali.context as ctx
from yali.gui import ScreenWidget
from yali.gui.Ui.installwidget import Ui_InstallWidget

from yali.gui.Ui.installprogress import Ui_InstallProgress
from pds.gui import PAbstractBox, BOTCENTER

(EventConfigure, EventInstall, EventSetProgress, EventError,
 EventAllFinished, EventPackageInstallFinished, EventRetry) = range(1001, 1008)


class InstallProgressWidget(PAbstractBox):

    def __init__(self, parent):
        PAbstractBox.__init__(self, parent)

        self.ui = Ui_InstallProgress()
        self.ui.setupUi(self)

        self._animation = 2
        self._duration = 500

    def showInstallProgress(self):
        QTimer.singleShot(
            1, lambda: self.animate(start=BOTCENTER, stop=BOTCENTER))

    """
    def hideHelp(self):
            self.animate(start = CURRENT,
                         stop  = TOPCENTER,
                         direction = OUT)
    def toggleHelp(self):
        if self.isVisible():
            self.hideHelp()
        else:
            self.showHelp()

    def setHelp(self, help):
        self.ui.helpContent.hide()
        self.ui.helpContent2.setText(help)
        # self.resize(QSize(1,1))
        QTimer.singleShot(1, self.adjustSize)
    """


def iter_slideshows():
    slideshows = []

    release_file = os.path.join(
        ctx.consts.branding_dir, ctx.flags.branding, ctx.consts.release_file)
    slideshows_content = yali.util.parse_branding_slideshows(release_file)

    for content in slideshows_content:
        slideshows.append({"picture": QPixmap(os.path.join(
            ctx.consts.branding_dir,
            ctx.flags.branding,
            ctx.consts.slideshows_dir,
            content[0])), "description": content[1]})
    while True:
        for slideshow in slideshows:
            yield slideshow


class Widget(QWidget, ScreenWidget):
    name = "packageInstallation"

    def __init__(self):
        QWidget.__init__(self)
        self.ui = Ui_InstallWidget()
        self.ui.setupUi(self)

        self.installProgress = InstallProgressWidget(self)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.changeSlideshows)

        self.poll_timer = QTimer(self)
        self.poll_timer.timeout.connect(self.checkQueueEvent)

        if ctx.lang == "tr":
            self.installProgress.ui.progress.setFormat("%%p")

        self.iter_slideshows = iter_slideshows()

        # show first pic
        self.changeSlideshows()

        self.total = 0
        self.cur = 0
        self.has_errors = False

        # mutual exclusion
        self.mutex = None
        self.wait_condition = None
        self.queue = None

        self.retry_answer = False
        self.pkg_configurator = None
        self.pkg_installer = None

    def shown(self):
        # Disable mouse handler
        ctx.mainScreen.dontAskCmbAgain = True
        ctx.mainScreen.theme_shortcut.setEnabled(False)
        ctx.mainScreen.ui.system_menu.setEnabled(False)

        # start installer thread
        ctx.logger.debug("PkgInstaller is creating...")
        self.mutex = QMutex()
        self.wait_condition = QWaitCondition()
        self.queue = Queue()
        self.pkg_installer = SqfsInstaller(
            self.queue, self.mutex, self.wait_condition, self.retry_answer)

        self.poll_timer.start(500)

        # start installer polling
        ctx.logger.debug("Calling PkgInstaller.start...")
        self.pkg_installer.start()

        ctx.mainScreen.disableNext()
        ctx.mainScreen.disableBack()

        # start 30 seconds
        self.timer.start(1000 * 30)

        self.installProgress.showInstallProgress()

    def checkQueueEvent(self):

        while True:
            try:
                data = self.queue.get_nowait()
                event = data[0]
            except Empty:
                return

            ctx.logger.debug("checkQueueEvent: Processing %s event..." % event)
            # EventInstall
            if event == EventInstall:
                # FIXME: mesajlar düzenlenecek
                info = data[1]
                percent = info["percent"]
                # percent = data[1]
                self.installProgress.ui.info.setText(
                    _("General",
                      # "Installing <b>{percent:.2f}%</b>".format(percent=percent)))
                      "Installing <b>{percent:.2f}%</b> : {file}".format(**info)))
                if percent >= self.cur + 0.5:
                    ctx.logger.debug("Sqfs: installing {}%".format(percent))
                self.cur = percent
                self.installProgress.ui.progress.setValue(self.cur)

            # EventConfigure
            elif event == EventConfigure:
                package = data[1]
                self.installProgress.ui.info.setText(
                    _("General", "Configuring <b>%s</b>") % package.name)
                ctx.logger.debug("Pisi: %s configuring" % package.name)
                self.cur += 1
                self.installProgress.ui.progress.setValue(self.cur)

            # EventSetProgress
            elif event == EventSetProgress:
                total = data[1]
                self.installProgress.ui.progress.setMaximum(total)

            # EventPackageInstallFinished
            elif event == EventPackageInstallFinished:
                # print("***EventPackageInstallFinished called....")
                # self.packageInstallFinished()
                self.sqfsInstallFinished()
                event = EventAllFinished

            # EventError
            elif event == EventError:
                err = data[1]
                self.installError(err)

            # EventRetry
            elif event == EventRetry:
                package = os.path.basename(data[1])
                self.timer.stop()
                self.poll_timer.stop()
                rc = ctx.interface.messageWindow(
                    _("General", "Warning"),
                    _("General", "Following error occured while "
                        "installing packages:"
                        "<b>%s</b><br><br>"
                        "Do you want to retry?")
                    % package,
                    type="custom", customIcon="warning",
                    customButtons=[_("General", "Yes"), _("General", "No")])
                self.retry_answer = not rc

                self.timer.start(1000 * 30)
                self.poll_timer.start(500)
                self.wait_condition.wakeAll()

            # EventAllFinished
            if event == EventAllFinished:
                self.finished()

    def changeSlideshows(self):
        slide = self.iter_slideshows.next()
        self.ui.slideImage.setPixmap(slide["picture"])
        # if slide["description"].has_key(ctx.lang):
        if ctx.lang in slide["description"]:
            description = slide["description"][ctx.lang]
        else:
            description = slide["description"]["en"]
        self.ui.slideText.setText(description)

    def sqfsInstallFinished(self):
        # bilgi yazısı kontrol edilecek
        self.installProgress.setVisible(False)
        ctx.interface.informationWindow.update(
            message=_("General", "Fstab, grub configuration, etc is writing."))
        yali.postinstall.writeFstab()

        # Configure Pending...
        # run baselayout's postinstall first
        yali.postinstall.initbaselayout()

        # postscripts depend on 03locale...
        yali.util.writeLocaleFromCmdline()

        # Write InitramfsConf
        yali.postinstall.writeInitramfsConf()

        # set resume param in /etc/default/grub
        yali.postinstall.setGrubResume()

        # copy needed files
        # yali.util.cp("/etc/resolv.conf", "%s/etc/" % ctx.consts.target_dir)

        ctx.interface.informationWindow.update(
            message=_("General",
                      "Unnecessary files and packages are being removed."))
        # run dbus in chroot
        yali.util.start_dbus()
        kver = ".".join(os.uname()[2].split(".")[:2])
        yali.util.run_batch(
            "rm -rf {}/etc/modules.autoload.d/kernel-{}".format(
                ctx.consts.target_dir, kver))

        yali.util.run_batch(
            "rm -rf {}/etc/polkit-1/localauthority/90-mandatory.d/".format(
                ctx.consts.target_dir))
        yali.util.run_batch(
            "rm -rf {}/run/livemedia".format(ctx.consts.target_dir))
        # mount -B /run/udev target_dir/run/udev
        yali.util.chroot("pisi it --rei --ignore-file-conflicts \
            /var/cache/pisi/packages/*.pisi")
        yali.util.run_batch(
            "rm -rf {}/var/cache/pisi/packages/*.pisi".format(
                ctx.consts.target_dir))

        yali.util.chroot("pisi rm --purge yali yali-branding-pisilinux \
            yali-theme-pisilinux xdm")
        yali.util.run_batch(
            "rm -rf {}/usr/share/applications/yali*.desktop".format(
                ctx.consts.target_dir))

        # WARNING: çalışmadı tekrar dene
        yali.util.run_batch(
            "cp -f /etc/resolv.conf {}/etc/resolv.conf".format(
                ctx.consts.target_dir))

        ctx.interface.informationWindow.update(
            message=_("General",
                      "Paket depoları ayarlanıyor."))

        yali.pisiiface.initialize2(with_comar=True)
        yali.pisiiface.switchToPardusRepo("live")

        # sddm_conf = "{}/etc/sddm.conf".format(ctx.consts.target_dir)
        # if os.path.exists(sddm_conf):
        #     import ConfigParser
        #     cfg = ConfigParser.ConfigParser()
        #     cfg.optionxform = str
        #
        #     cfg.read(sddm_conf)
        #
        #     cfg.set("Autologin", "Session", "")
        #     cfg.set("Autologin", "User", "")
        #
        #     with open(sddm_conf, "w") as f:
        #         cfg.write(f)

        # root oto giriş iptali için /etc/inittab dosyasında düzenleme
        yali.util.dosed(
            "{}/etc/inittab".format(ctx.consts.target_dir),
            "(.*) --autologin root (tty[1|2])", "\\1 \\2")
        yali.util.dosed(
            "{}/etc/inittab".format(ctx.consts.target_dir),
            "(.*) --noclear --autologin root (tty[3-6])", "\\1 \\2")

    def packageInstallFinished(self):
        yali.postinstall.writeFstab()

        # Configure Pending...
        # run baselayout's postinstall first
        yali.postinstall.initbaselayout()

        # postscripts depend on 03locale...
        yali.util.writeLocaleFromCmdline()

        # Write InitramfsConf
        yali.postinstall.writeInitramfsConf()

        # set resume param in /etc/default/grub
        yali.postinstall.setGrubResume()

        # run dbus in chroot
        yali.util.start_dbus()

        # start configurator thread
        self.pkg_configurator = PkgConfigurator(self.queue, self.mutex)
        self.pkg_configurator.start()

    def execute(self):
        # stop slide show
        self.timer.stop()
        self.poll_timer.stop()
        return True

    def finished(self):
        self.poll_timer.stop()

        if self.has_errors:
            return

        ctx.mainScreen.slotNext()

    def installError(self, error):
        self.has_errors = True
        errorstr = _("General",
                     """An error occured during the installation of packages.
This may be caused by a corrupted installation medium error:
%s
""") % str(error)
        ctx.interface.exceptionWindow(error, errorstr)
        ctx.logger.error("Package installation failed error with:%s" % error)


# FIXME: sınıf tamamlanacak
class SqfsInstaller(Process):
    def __init__(self, queue, mutex, wait_condition, retry_answer):
        Process.__init__(self)
        self.queue = queue
        self.mutex = mutex
        self.wait_condition = wait_condition
        self.retry_answer = retry_answer
        ctx.logger.debug("SqfsInstaller started.")

    def run(self):
        ctx.logger.debug("PkgInstaller is running.")
        ui = SqfsUI(self.queue)
        ui.run()
        ctx.logger.debug("PisiUI is creating..")
        ctx.logger.debug("Pisi initialize is calling..")

        data = [EventPackageInstallFinished]
        self.queue.put_nowait(data)


class SqfsUI:

    def __init__(self, queue):
        self.queue = queue
        self.percent = 0
        self.info = {"percent": 0, "file": ""}

        yali.util.run_batch("mkdir /mnt/sqfs")
        yali.util.run_batch("mount {} /mnt/sqfs".format(ctx.consts.sqfs_file))

    def notify(self, **keywords):
        ctx.logger.debug("SqfsUI.notify event: Install")
        data = [EventInstall, self.info]
        self.queue.put_nowait(data)

    def run(self):
        total = 100
        ctx.logger.debug("Sending EventSetProgress")
        data = [EventSetProgress, total]
        self.queue.put_nowait(data)

        process = subprocess.Popen(
            "unsquashfs -l {sqfs} | wc -l".format(
                sqfs=ctx.consts.sqfs_file),
            shell=True, stdout=subprocess.PIPE)
        total = float(int(process.communicate()[0].rstrip()) - 3)

        rsync_env = os.environ.copy()
        rsync_env['LC_ALL'] = "C"
        process = subprocess.Popen(
            "rsync -aHAXr --progress {sqfs_dir}/* {dir}".format(
                dir=ctx.consts.target_dir,
                sqfs_dir="/mnt/sqfs"), env=rsync_env,
            shell=True, stdout=subprocess.PIPE)

        count = 0
        for line in iter(process.stdout.readline, b''):
            try:
                if (line[0] in letters) or line[0] == "\\":
                    line = line.rstrip()
                    count += 1
                    self.percent = count / total * 100
                    if self.percent > 100:
                        self.percent = 100.0
                    # print(self.percent, count, total)
                    # TODO: sondaki ilgisiz 3 satır atlanacak!
                    self.info = {"percent": self.percent, "file": line}
            except Exception as e:
                self.error(e)
            self.notify()

        self.percent = 100
        self.notify()
        yali.util.run_batch("umount /mnt/sqfs")

    def error(self, msg):
        ctx.logger.debug("SqfsUI.error: %s" % unicode(msg))

    def warning(self, msg):
        ctx.logger.debug("SqfsUI.warning: %s" % unicode(msg))


class PkgInstaller(Process):

    def __init__(self, queue, mutex, wait_condition, retry_answer):
        Process.__init__(self)
        self.queue = queue
        self.mutex = mutex
        self.wait_condition = wait_condition
        self.retry_answer = retry_answer
        ctx.logger.debug("PkgInstaller started.")

    def run(self):
        ctx.logger.debug("PkgInstaller is running.")
        ui = PisiUI(self.queue)
        ctx.logger.debug("PisiUI is creating..")
        yali.pisiiface.initialize(ui)
        ctx.logger.debug("Pisi initialize is calling..")

        if ctx.flags.collection:
            ctx.logger.debug("Collection Repo added.")
            yali.pisiiface.addRepo(
                ctx.consts.collection_repo_name,
                ctx.installData.autoCollection.index)
        else:
            ctx.logger.debug("CD Repo adding.")
            yali.pisiiface.addCdRepo()

        # show progress
        total = len(ctx.packagesToInstall)
        ctx.logger.debug("Sending EventSetProgress")
        data = [EventSetProgress, total*2]
        self.queue.put_nowait(data)
        ctx.logger.debug("Found %d packages in repo.." % total)
        try:
            while True:
                try:
                    yali.pisiiface.install(ctx.packagesToInstall)
                    break  # while
                except Exception as msg:
                    # Lock the mutex
                    self.mutex.lock()

                    # Send error message
                    data = [EventRetry, str(msg)]
                    self.queue.put_nowait(data)

                    # wait for the result
                    self.wait_condition.wait(self.mutex)
                    self.mutex.unlock()

                    if not self.retry_answer:
                        raise msg

        except Exception as msg:
            data = [EventError, msg]
            self.queue.put_nowait(data)
            # wait for the result
            self.wait_condition.wait(self.mutex)

        ctx.logger.debug("Package install finished ...")
        # Package Install finished lets configure them
        data = [EventPackageInstallFinished]
        self.queue.put_nowait(data)


class PkgConfigurator(Process):

    def __init__(self, queue, mutex):
        Process.__init__(self)
        self.queue = queue
        self.mutex = mutex
        ctx.logger.debug("PkgConfigurator started.")

    def run(self):
        ctx.logger.debug("PkgConfigurator is running.")
        ui = PisiUI(self.queue)
        yali.pisiiface.initialize(ui=ui, with_comar=True)

        try:
            # run all pending...
            ctx.logger.debug("exec : yali.pisiiface.configurePending() called")
            yali.pisiiface.configurePending()
        except Exception as msg:
            data = [EventError, msg]
            self.queue.put_nowait(data)

        # Remove temporary repository and install add real
        if ctx.flags.collection:
            yali.pisiiface.switchToPardusRepo(ctx.consts.collection_repo_name)
        else:
            yali.pisiiface.switchToPardusRepo(ctx.consts.cd_repo_name)

        data = [EventAllFinished]
        self.queue.put_nowait(data)


class PisiUI(pisi.ui.UI):

    def __init__(self, queue):
        pisi.ui.UI.__init__(self)
        self.queue = queue
        self.last_package = ''

    def notify(self, event, **keywords):
        if event == pisi.ui.installing:
            ctx.logger.debug("PisiUI.notify event: Install")
            data = [EventInstall, keywords['package']]
            self.last_package = keywords['package'].name
            self.queue.put_nowait(data)
        elif event == pisi.ui.configuring:
            ctx.logger.debug("PisiUI.notify event: Configure")
            data = [EventConfigure, keywords['package']]
            self.last_package = keywords['package'].name
            self.queue.put_nowait(data)

    def error(self, msg):
        ctx.logger.debug("PisiUI.error: %s" % unicode(msg))

    def warning(self, msg):
        ctx.logger.debug("PisiUI.warning: %s" % unicode(msg))
