#!/usr/bin/python
# -*- coding: utf-8 -*-

import pds.container
try:
    from PyQt5.QtCore import QCoreApplication
    _ = QCoreApplication.translate
except:
    _ = lambda x,y: y

from PyQt5.QtWidgets import QWidget, QGridLayout
from PyQt5.Qt import pyqtSignal

import yali.context as ctx
from yali.gui import ScreenWidget

class Widget(QWidget, ScreenWidget):
    name = "network"

    def __init__(self):
        QWidget.__init__(self)
        self.layout = QGridLayout(self)
        self.networkConnector = pds.container.PNetworkManager(self)
        self.layout.addWidget(self.networkConnector)

    def shown(self):
        self.networkConnector.startNetworkManager()

    def execute(self):
        self.networkConnector._proc.terminate()
        ctx.mainScreen.disableBack()
        return True
    


