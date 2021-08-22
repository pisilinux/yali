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
import sys
import imp

try:
    from PyQt5.QtCore import QCoreApplication
    _ = QCoreApplication.translate
except:
    _ = lambda x,y: y

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QStyleFactory
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QShortcut
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import QTranslator
from PyQt5.QtCore import QLocale
from PyQt5.QtCore import QLibraryInfo
from PyQt5.QtWidgets import QWidget

import yali
import yali.util
import yali.context as ctx
import yali.gui
import yali.gui.YaliWindow


class Runner():

    _window = None
    _application = None

    def __init__(self, app=None):

        if app is None:
            self._application = QApplication(sys.argv)
        else:
            self._application = app
        self._window = None

        # Main Window Initialized..
        try:
            self._window = yali.gui.YaliWindow.Widget()
        except yali.Error, msg:
            print("error")
            ctx.logger.debug(msg)
            sys.exit(1)

        # self._translator = QTranslator()
        # self._translator.load("qt_" + QLocale.system().name(), QLibraryInfo.location(QLibraryInfo.TranslationsPath))
        # print(QLocale.system().name())
        # print(QLibraryInfo.location(QLibraryInfo.TranslationsPath))

        ctx.mainScreen = self._window
        # print(type(self._window))
        screens = self._get_screens(ctx.flags.install_type)
        self._set_steps(screens)

        # These shorcuts for developers :)
        prevScreenShortCut = QShortcut(QKeySequence(Qt.SHIFT + Qt.Key_F1), self._window)
        nextScreenShortCut = QShortcut(QKeySequence(Qt.SHIFT + Qt.Key_F2), self._window)
        prevScreenShortCut.activated.connect(self._window.slotBack)
        nextScreenShortCut.activated.connect(self._window.slotNext)

        # VBox utils
        ctx.logger.debug("Starting VirtualBox tools..")
        # FIXME:sh /etc/X11/Xsession.d/98-vboxclient.sh
        yali.util.run_batch("VBoxClient", ["--autoresize"])
        yali.util.run_batch("VBoxClient", ["--clipboard"])

        # Cp Reboot, ShutDown
        yali.util.run_batch("cp", ["/sbin/reboot", "/tmp/reboot"])
        yali.util.run_batch("cp", ["/sbin/shutdown", "/tmp/shutdown"])

        # base connections
        self._application.lastWindowClosed.connect(self._application.quit)
        self._window.signalProcessEvents.connect(self._application.processEvents)  # hata olabilir
        self._application.desktop().resized[int].connect(self._reinit_screen)  # hata olabilir

        # Font Resize
        fontMinusShortCut = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_Minus), self._window)
        fontPlusShortCut = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_Plus), self._window)
        fontMinusShortCut.activated.connect(self._window.setFontMinus)
        fontPlusShortCut.activated.connect(self._window.setFontPlus)

    def _reinit_screen(self):
        QTimer.singleShot(700, self._init_screen)

    def _init_screen(self):
        # We want it to be a full-screen window
        # inside the primary display.
        screen = self._application.desktop().screenGeometry()
        # canlı iso kurulumda tam ekran olmamalı
        if os.path.exists("/usr/bin/xdm"):
            self._window.resize(screen.size())
        else:
            self._window.setMaximumSize(screen.size())
            # FIXME: ui dosyasları görsellik açin yeniden düzenlenmeli
            self._window.setGeometry(0,0,1120,630)

        #self._window.move(screen.topLeft())
        self._window.show()

    def _get_screens(self, install_type):
        screens = []
        ctx.logger.info("Install type is %s" % ctx.STEP_TYPE_STRINGS[install_type])
        for name in yali.gui.GUI_STEPS[install_type]:
            screenClass = None
            moduleName = ""
            try:
                module_name  = yali.gui.stepToClass[name]
                found = imp.find_module(module_name, yali.gui.__path__)
                loaded = imp.load_module(module_name, *found)
                screenClass = loaded.__dict__["Widget"]

            except ImportError, msg:
                ctx.logger.debug(msg)
                rc = ctx.interface.messageWindow(_("General", "Error!"),
                                                 _("General", "An error occurred when attempting "
                                                   "to load an installer interface "
                                                   "component.\n\nclassName = %s.Widget") % module_name,
                                                 type="custom", customIcon="warning",
                                                 customButtons=[_("General", "Exit"), _("General", "Retry")])

                if not rc:
                    sys.exit(1)
            else:
                screens.append(screenClass)

        return screens


    def _set_steps(self, screens):
        self._window.createWidgets(screens)
        self._window.setCurrent(ctx.flags.startup)

    def run(self):
        # Use default theme;
        # if you use different Qt4 theme our works looks ugly :)
        self._application.setStyle(QStyleFactory.create('Brezee'))
        self._init_screen()

        # self._application.installTranslator(self._translator)

        # For testing..
        # self._window.resize(QSize(800,600))
        # print(dir(self._window))
        # Run run run
        self._window.show()
        self._application.exec_()
