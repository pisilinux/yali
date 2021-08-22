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
try:
    from PyQt5.QtCore import QCoreApplication
    _ = QCoreApplication.translate
except Exception:
    _ = lambda x,y: y
import pardus.xorg


from PyQt5.QtWidgets import (QWidget, QLineEdit, QListWidgetItem)#, QFocusEvent
from PyQt5.QtCore import (QTimeLine, QEvent)  # pyqtSignal,
from PyQt5.QtGui import (QIcon, QPixmap)


import yali.users
import yali.postinstall
import yali.context as ctx
from yali.gui import ScreenWidget
from yali.gui.Ui.setupuserswidget import Ui_SetupUsersWidget


class Widget(QWidget, ScreenWidget):
    name = "accounts"

    def __init__(self):
        super(Widget, self).__init__()
        self.ui = Ui_SetupUsersWidget()
        self.ui.setupUi(self)

        self.edititemindex = None

        self.time_line = QTimeLine(400, self)
        self.time_line.setFrameRange(0, 220)
        self.time_line.frameChanged[int].connect(self.animate)

        self.ui.scrollArea.setFixedHeight(0)

        # User Icons
        self.normal_user_icon = QPixmap(":/gui/pics/users.png")
        self.super_user_icon = QPixmap(":/gui/pics/users.png")

        # Set disabled the create Button
        self.ui.createButton.setEnabled(False)

        # Connections
        self.ui.pass1.textChanged[str].connect(self.slotTextChanged)
        self.ui.pass2.textChanged[str].connect(self.slotTextChanged)
        self.ui.username.textChanged[str].connect(self.slotTextChanged)
        self.ui.realname.textChanged[str].connect(self.slotTextChanged)
        self.ui.username.textEdited[str].connect(self.slotUserNameChanged)
        self.ui.realname.textEdited[str].connect(self.slotRealNameChanged)
        self.ui.userID.valueChanged[int].connect(self.slotTextChanged)
        self.ui.userIDCheck.stateChanged[int].connect(self.slotuserIDCheck)
        self.ui.createButton.clicked.connect(self.slotCreateUser)
        self.ui.cancelButton.clicked.connect(self.resetWidgets)
        self.ui.deleteButton.clicked.connect(self.slotDeleteUser)
        self.ui.editButton.clicked.connect(self.slotEditUser)
        self.ui.addMoreUsers.clicked.connect(self.slotAdvanced)
        self.ui.userList.itemDoubleClicked[QListWidgetItem].connect(self.slotEditUser)
        self.ui.pass2.returnPressed.connect(self.slotReturnPressed)

        # focusInEvent is not a signal
        # self.ui.pass1.focusInEvent[QFocusEvent].connect(self.checkCapsLock)
        # self.ui.pass2.focusInEvent[QFocusEvent].connect(self.checkCapsLock)
        # self.ui.username.focusInEvent[QFocusEvent].connect(self.checkCapsLock)
        # self.ui.realname.focusInEvent[QFocusEvent].connect(self.checkCapsLock)

        ctx.installData.users = []
        ctx.installData.autoLoginUser = None
        self.user_name_changed = False
        self.used_ids = []

    def eventFilter(self, obj, event):
        if event.type() == QEvent.FocusIn:  # even.type() ==...
            if obj == self.ui.pass1 or obj == self.ui.pass2 or \
                    obj == self.ui.username or obj == self.ui.realname:
                self.checkCapsLock()

    def shown(self):
        self.ui.cancelButton.hide()
        self.ui.realname.setFocus()
        if len(yali.users.PENDING_USERS) > 0 and self.ui.userList.count() == 0:
            for u in yali.users.PENDING_USERS:
                pix = self.normal_user_icon
                if "wheel" in u.groups:
                    pix = self.super_user_icon
                UserItem(self.ui.userList, pix, user=u)
                self.ui.autoLogin.addItem(u.username)
        if len(yali.users.PENDING_USERS) == 1:
            self.slotEditUser(self.ui.userList.item(0))
        elif len(yali.users.PENDING_USERS) > 1:
            self.ui.addMoreUsers.setChecked(True)
        self.checkUsers()
        self.checkCapsLock()

    def backCheck(self):
        self.refill()
        self.ui.cancelButton.hide()
        return True

    def refill(self):
        # reset and fill PENDING_USERS
        yali.users.reset_pending_users()
        for index in range(self.ui.userList.count()):
            user = self.ui.userList.item(index).getUser()
            ctx.installData.users.append(user)
            yali.users.PENDING_USERS.append(user)

    def execute(self):
        if self.checkUsers():
            ctx.installData.autoLoginUser = str(self.ui.autoLogin.currentText())
            if self.ui.createButton.text() == _("General", "Update"):
                return self.slotCreateUser()
            return True

        if not self.slotCreateUser():
            ctx.mainScreen.step_increment = 0
            return True

        self.refill()
        ctx.interface.informationWindow.hide()
        ctx.installData.autoLoginUser = str(self.ui.autoLogin.currentText())

        return True

    def setCapsLockIcon(self, child):
        if type(child) == QLineEdit:
            if pardus.xorg.capslock.isOn():
                child.setStyleSheet("""QLineEdit {
                        background-image: url(:/gui/pics/caps.png);
                        background-repeat: no-repeat;
                        background-position: right;
                        padding-right: 35px;
                        }""")
            else:
                child.setStyleSheet("""QLineEdit {
                        background-image: none;
                        padding-right: 0px;
                        }""")


    def checkCapsLock(self):
        for child in self.ui.groupBox.children():
            self.setCapsLockIcon(child)
        for child in self.ui.groupBox_2.children():
            self.setCapsLockIcon(child)

    def keyReleaseEvent(self, e):
        self.checkCapsLock()

    def showError(self, message):
        ctx.interface.informationWindow.update(message, type="error")
        ctx.mainScreen.disableNext()

    def animate(self, value):
        self.ui.scrollArea.setFixedHeight(int(value))
        self.ui.frame.setMinimumHeight(250)

        if self.ui.scrollArea.height() == 0:
            self.ui.scrollArea.hide()
        else:
            self.ui.scrollArea.show()

        if self.ui.scrollArea.height() == 220:
            self.time_line.setDirection(1)
            self.ui.frame.setMinimumHeight(420)
        if self.ui.scrollArea.height() == 0:
            self.time_line.setDirection(0)

    def slotuserIDCheck(self, state):
        if state:
            self.ui.userID.setEnabled(True)
        else:
            self.ui.userID.setEnabled(False)

    def slotAdvanced(self):
        icon_path = None
        if self.ui.scrollArea.isVisible():
            icon_path = ":/gui/pics/expand.png"
            self.time_line.start()
        else:
            self.ui.scrollArea.show()
            icon_path = ":/gui/pics/collapse.png"
            self.time_line.start()

        icon = QIcon()
        icon.addPixmap(QPixmap(icon_path), QIcon.Normal, QIcon.Off)
        self.ui.addMoreUsers.setIcon(icon)
        self.checkUsers()

    def slotTextChanged(self):
        username = str(self.ui.username.text())
        realname = unicode(self.ui.realname.text())
        password = unicode(self.ui.pass1.text())
        password_confirm = unicode(self.ui.pass2.text())

        if not password == '' and (password.lower() == username.lower() or
                                   password.lower() == realname.lower()):
            self.showError(_("General", 'Don\'t use your user name or name as a password'))
            return
        elif password_confirm != password and password_confirm:
            self.showError(_("General", 'Passwords do not match'))
            return
        elif len(password) == len(password_confirm) and len(password_confirm) < 4 and not password =='':
            self.showError(_("General", 'Password is too short'))
            return
        else:
            ctx.interface.informationWindow.hide()

        if self.ui.username.text() and password and password_confirm:
            self.ui.createButton.setEnabled(True)
            if not self.ui.addMoreUsers.isChecked():
                ctx.mainScreen.enableNext()
                ctx.mainScreen.enableBack()
        else:
            self.ui.createButton.setEnabled(False)
            if not self.ui.addMoreUsers.isChecked():
                ctx.mainScreen.disableNext()

    def currentUsers(self):
        users = []
        for index in range(self.ui.userList.count()):
            users.append(self.ui.userList.item(index).getUser().username)
        return users

    def slotUserNameChanged(self):
        self.user_name_changed = True

    def slotRealNameChanged(self):
        if not self.user_name_changed:
            used_users = yali.users.get_users()
            used_users.extend(self.currentUsers())
            self.ui.username.setText(yali.users.nick_guess(self.ui.realname.text(), used_users))

    def slotCreateUser(self):
        user = yali.users.User()
        user.username = str(self.ui.username.text())
        # ignore last character. see bug #887
        user.realname = unicode(self.ui.realname.text())
        user.passwd = unicode(self.ui.pass1.text())
        user.groups = ["users", "pnp", "disk", "audio", "video", "power",
                     "dialout", "lp", "lpadmin", "cdrom", "floppy"]
        pix = self.normal_user_icon
        if self.ui.admin.isChecked():
            user.groups.append("wheel")
            pix = self.super_user_icon
        user.no_password = self.ui.noPass.isChecked()

        # check user validity
        if user.exists() or (user.username in self.currentUsers() and self.edititemindex == None):
            self.showError(_("General", "This user name is already taken, please choose another one."))
            return False
        elif not user.usernameIsValid():
            # FIXME: Mention about what are the invalid characters!
            self.showError(_("General", "The user name contains invalid characters."))
            return False
        elif not user.realnameIsValid():
            self.showError(_("General", "The real name contains invalid characters."))
            return False

        # Dont check in edit mode
        if self.ui.addMoreUsers.isChecked() and self.ui.userIDCheck.isChecked():
            uid = self.ui.userID.value()
            if self.edititemindex == None:
                if uid in self.used_ids:
                    self.showError(_("General", 'User ID used before, choose another one!'))
                    return False
            self.used_ids.append(uid)
            user.uid = uid

        self.ui.createButton.setText(_("General", "Add"))
        self.ui.cancelButton.hide()
        update_item = None

        try:
            self.ui.userList.takeItem(self.edititemindex)
            self.ui.autoLogin.removeItem(self.edititemindex + 1)
        except:
            update_item = self.edititemindex
            # nothing wrong. just adding a new user...
            pass

        item = UserItem(self.ui.userList, pix, user=user)

        # add user to auto-login list.
        self.ui.autoLogin.addItem(user.username)

        if update_item:
            self.ui.autoLogin.setCurrentIndex(self.ui.autoLogin.count())

        # clear form
        self.resetWidgets()

        ctx.logger.debug("slotCreateUser :: user (%s) '%s (%s)' added/updated" % (user.uid, user.realname, user.username))
        ctx.logger.debug("slotCreateUser :: user groups are %s" % str(','.join(user.groups)))

        # give focus to realname widget for a new user. #3280
        #self.ui.realname.setFocus()
        self.checkUsers()
        self.user_name_changed = False
        self.refill()
        return True

    def slotDeleteUser(self):
        if self.ui.userList.currentRow() == self.edititemindex:
            self.resetWidgets()
            self.ui.autoLogin.setCurrentIndex(0)
        _cur = self.ui.userList.currentRow()
        item = self.ui.userList.item(_cur).getUser()
        if item.uid in self.used_ids:
            self.used_ids.remove(item.uid)
        self.ui.userList.takeItem(_cur)
        self.ui.autoLogin.removeItem(_cur + 1)
        self.ui.createButton.setText(_("General", "Add"))

        icon = QIcon()
        icon.addPixmap(QPixmap(":/gui/pics/user-group-new.png"), QIcon.Normal, QIcon.Off)
        self.ui.createButton.setIcon(icon)

        self.ui.cancelButton.hide()
        self.checkUsers()

    def slotEditUser(self, item=None):
        if not item:
            item = self.ui.userList.currentItem()
        self.ui.userList.setCurrentItem(item)
        user = item.getUser()
        if user.uid > -1:
            self.ui.userIDCheck.setChecked(True)
            self.ui.userID.setValue(user.uid)
        self.ui.username.setText(user.username)
        self.ui.realname.setText(user.realname)
        self.ui.pass1.setText(user.passwd)
        self.ui.pass2.setText(user.passwd)

        if "wheel" in user.groups:
            self.ui.admin.setChecked(True)
        else:
            self.ui.admin.setChecked(False)

        self.ui.noPass.setChecked(user.no_password)

        self.edititemindex = self.ui.userList.currentRow()
        self.ui.createButton.setText(_("General", "Update"))
        icon = QIcon()
        icon.addPixmap(QPixmap(":/gui/pics/tick.png"), QIcon.Normal, QIcon.Off)
        self.ui.createButton.setIcon(icon)
        self.ui.cancelButton.setVisible(self.ui.createButton.isVisible())

    def checkUserFields(self):
        username = unicode(self.ui.username.text())
        realname = unicode(self.ui.realname.text())
        password = unicode(self.ui.pass1.text())
        password_confirm = unicode(self.ui.pass2.text())
        if username and realname and password and password_confirm and \
        (password == password_confirm) and \
        (password.lower() != username.lower() and password.lower() != realname.lower()):
            return True
        else:
            return False

    def checkUsers(self):
        if self.ui.userList.count() > 0:
            self.ui.userList.setCurrentRow(0)
            self.ui.deleteButton.setEnabled(True)
            self.ui.editButton.setEnabled(True)
            self.ui.autoLogin.setEnabled(True)
            ctx.mainScreen.enableNext()
            ctx.mainScreen.enableBack()
            return True
        else:
            if self.checkUserFields():
                ctx.mainScreen.enableNext()
            else:
                ctx.mainScreen.disableNext()

        # there is no user in list so noting to delete
        self.ui.deleteButton.setEnabled(False)
        self.ui.editButton.setEnabled(False)
        self.ui.autoLogin.setEnabled(False)
        return False


    def resetWidgets(self):
        # clear all
        self.edititemindex = None
        self.ui.username.clear()
        self.ui.realname.clear()
        self.ui.pass1.clear()
        self.ui.pass2.clear()
        self.ui.admin.setChecked(False)
        self.ui.noPass.setChecked(False)
        self.ui.userIDCheck.setChecked(False)
        self.ui.createButton.setEnabled(False)
        if self.ui.cancelButton.isVisible():
            self.ui.cancelButton.setHidden(self.sender() == self.ui.cancelButton)
            self.checkUsers()
        self.ui.createButton.setText(_("General", "Add"))
        icon = QIcon()
        icon.addPixmap(QPixmap(":/gui/pics/user-group-new.png"), QIcon.Normal, QIcon.Off)
        self.ui.createButton.setIcon(icon)


    def slotReturnPressed(self):
        if self.ui.createButton.isEnabled() and self.ui.addMoreUsers.isChecked():
            self.slotCreateUser()

class UserItem(QListWidgetItem):

    ##
    # @param user (yali.users.User)
    def __init__(self, parent, pixmap, user):
        icon = QIcon(pixmap)
        QListWidgetItem.__init__(self, icon, user.username, parent)
        self._user = user

    def getUser(self):
        return self._user
