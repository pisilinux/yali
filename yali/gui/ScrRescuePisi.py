# -*- coding: utf-8 -*-
#
# Copyright (C) 2009-2010 TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import os
import dbus
import pisi
try:
    from PyQt5.QtCore import QCoreApplication
    _ = QCoreApplication.translate
except:
    _ = lambda x,y: y

from PyQt5.QtWidgets import QWidget, QListWidgetItem
from PyQt5.QtCore import pyqtSignal, QObject, QEvent
from PyQt5.QtGui import QIcon

import yali.util
import yali.pisiiface
import yali.postinstall
import yali.context as ctx
from yali.gui import ScreenWidget
from yali.gui.Ui.rescuepisiwidget import Ui_RescuePisiWidget
from yali.gui.Ui.connectionlist import Ui_connectionWidget

class Widget(QWidget, ScreenWidget):
    name = "pisiRescue"

    def __init__(self):
        QWidget.__init__(self)
        self.ui = Ui_RescuePisiWidget()
        self.ui.setupUi(self)
        self.steps = YaliSteps()
        self.steps.setOperations([{"text":_("General", "Starting D-Bus..."),"operation":yali.util.start_dbus},
                                  {"text":_("General", "Connecting to D-Bus..."),"operation":yali.postinstall.connectToDBus},
                                  {"text":_("General", "Fetching history..."),"operation":self.fillHistoryList}])

        self.ui.buttonSelectConnection.clicked.connect(self.showConnections)
        self.connectionWidget = None

    def showConnections(self):
        self.connectionWidget.show()

    def fillHistoryList(self):
        ui = PisiUI()
        ctx.logger.debug("PisiUI is creating..")
        yali.pisiiface.initialize(ui, with_comar = True)
        try:
            history = yali.pisiiface.getHistory()
            for hist in history:
                HistoryItem(self.ui.historyList, hist)
        except:
            return False
        return True

    def checkRegisteredConnections(self):
        self.connectionWidget = ConnectionWidget(self)
        registeredConnectionsTotal = 0
        for connection in self.connectionWidget.connections.values():
            registeredConnectionsTotal+=len(connection)

        return registeredConnectionsTotal

    def shown(self):
        self.ui.buttonSelectConnection.setEnabled(False)
        ctx.interface.informationWindow.update(_("General", "Please Wait..."))
        self.steps.slotRunOperations()
        ctx.interface.informationWindow.hide()
        if self.checkRegisteredConnections():
            self.ui.buttonSelectConnection.setEnabled(True)
        else:
            self.ui.labelStatus.setText(_("General", "No connection available"))

    def execute(self):
        ctx.takeBackOperation = self.ui.historyList.currentItem().getInfo()
        ctx.mainScreen.step_increment = 2
        return True

    def backCheck(self):
        ctx.mainScreen.step_increment = 2
        return True

class PisiUI(QObject, pisi.ui.UI):

    def __init__(self, *args):
        pisi.ui.UI.__init__(self)
        apply(QObject.__init__, (self,) + args)

    def notify(self, event, **keywords):
        ctx.logger.debug("PISI: Event %s %s" % (event, keywords))

    def display_progress(self, operation, percent, info, **keywords):
        ctx.logger.debug("PISI: %s %s %s" % (operation, percent, info))
        ctx.mainScreen.processEvents()

class PisiEvent(QEvent):

    def __init__(self, _, event):
        QEvent.__init__(self, _)
        self.event = event

    def eventType(self):
        return self.event

    def setData(self,data):
        self._data = data

    def data(self):
        return self._data

class HistoryItem(QListWidgetItem):
    def __init__(self, parent, info):
        QListWidgetItem.__init__(self, _("General", "Operation %(no)s : %(date)s - %(type)s") % {"no":info.no, "date":info.date, "type":info.type}, parent)
        self._info = info

    def getInfo(self):
        return self._info

class ConnectionItem(QListWidgetItem):
    def __init__(self, parent, connection, package):
        QListWidgetItem.__init__(self, QIcon(":/gui/pics/%s.png" % package), connection, parent)
        self._connection = [connection, package]

    def getConnection(self):
        return self._connection[0]

    def getPackage(self):
        return self._connection[1]

    def connect(self):
        connectTo(self.getPackage(), self.getConnection())

class ConnectionWidget(QWidget):

    def __init__(self, rootWidget):
        QWidget.__init__(self, ctx.mainScreen)
        self.ui = Ui_connectionWidget()
        self.ui.setupUi(self)
        self.setStyleSheet("""
                QFrame#mainFrame {
                    background-image: url(:/gui/pics/transBlack.png);
                    border: 1px solid #BBB;
                    border-radius:8px;
                }
                QWidget#autoPartQuestion {
                    background-image: url(:/gui/pics/trans.png);
                }
        """)

        self.rootWidget = rootWidget
        self.needsExecute = False
        self.ui.buttonCancel.clicked.connect(self.hide)
        self.ui.buttonConnect.clicked.connect(self.slotUseSelected)

        self.connections = getConnectionList()
        if self.connections:
            for package in self.connections.keys():
                for connection in self.connections[package]:
                    ci = ConnectionItem(self.ui.connectionList, unicode(str(connection)), package)

            self.ui.connectionList.setCurrentRow(0)
            self.resize(ctx.mainScreen.size())

    def slotUseSelected(self):
        current = self.ui.connectionList.currentItem()
        if current:
            ctx.interface.informationWindow.update(_("General", "Connecting to network %s...") % current.getConnection())

            try:
                ret = current.connect()
            except:
                ret = True
                self.rootWidget.ui.labelStatus.setText(_("General", "Connection failed"))
                ctx.interface.informationWindow.update(_("General", "Connection failed"))

            if not ret:
                self.rootWidget.ui.labelStatus.setText(_("General", "Connected"))
                ctx.interface.informationWindow.update(_("General", "Connected"))

            self.hide()
            ctx.mainScreen.processEvents()
            ctx.interface.informationWindow.hide()

            if self.needsExecute:
                self.rootWidget.execute_(True)


