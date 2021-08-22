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
except:
    _ = lambda x,y: y

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal, QVariant

import yali.util
import yali.localedata
import yali.postinstall
import yali.context as ctx
from yali.gui import ScreenWidget
from yali.gui.Ui.keyboardwidget import Ui_KeyboardWidget

##
# Keyboard setup screen
class Widget(QWidget, ScreenWidget):
    name = "keyboardSetup"

    def __init__(self):
        QWidget.__init__(self)
        self.ui = Ui_KeyboardWidget()
        self.ui.setupUi(self)

        index = 0 # comboBox.addItem doesn't increase the currentIndex
        self.default_layout_index = None
        locales = sorted([(country, data) for country, data in yali.localedata.locales.items()])
        for country, data in locales:
            if data["xkbvariant"]:
                i = 0
                for variant in data["xkbvariant"]:
                    _d = dict(data)
                    _d["xkbvariant"] = variant[0]
                    _d["name"] = variant[1]
                    _d["consolekeymap"] = data["consolekeymap"][i]
                    self.ui.keyboard_list.addItem(_d["name"], QVariant(_d))
                    i += 1
            else:
                self.ui.keyboard_list.addItem(data["name"], QVariant(data))
            if ctx.lang == country:
                if ctx.lang == "tr":
                    self.default_layout_index = index + 1
                else:
                    self.default_layout_index = index
            index += 1


        self.ui.keyboard_list.setCurrentIndex(self.default_layout_index)

        self.ui.keyboard_list.currentIndexChanged[int].connect(self.slotLayoutChanged)

        ctx.mainScreen.currentLanguageChanged.connect(self.retranslateUi)
        ctx.mainScreen.currentLanguageChanged.connect(self.changeCountry)

    def changeCountry(self):
        countries = sorted([country for country in yali.localedata.locales.keys()])

        index = countries.index(ctx.lang.split("_")[0])


        if ctx.lang == "tr":
            self.default_layout_index = index + 1
        else:
            self.default_layout_index = index


        self.ui.keyboard_list.setCurrentIndex(self.default_layout_index)


    def shown(self):
        self.slotLayoutChanged()

    def slotLayoutChanged(self):
        index = self.ui.keyboard_list.currentIndex()
        keymap = self.ui.keyboard_list.itemData(index)#.toMap()
        # Gökmen's converter
        # keymap = dict(map(lambda x: (str(x[0]), unicode(x[1])), keymap.iteritems()))
        keymap = dict(map(lambda x: (str(x[0]), x[1]), keymap.iteritems()))
        ctx.installData.keyData = keymap
        ctx.interface.informationWindow.hide()
        if "," in keymap["xkblayout"]:
            message = _("General", "Use Alt-Shift to toggle between alternative keyboard layouts")
            ctx.interface.informationWindow.update(message, type="warning")
        else:
            ctx.interface.informationWindow.hide()

        yali.util.setKeymap(keymap["xkblayout"], keymap["xkbvariant"])

    def execute(self):
        ctx.interface.informationWindow.hide()
        ctx.logger.debug("Selected keymap is : %s" % ctx.installData.keyData["name"])
        return True

    def retranslateUi(self):
        self.ui.retranslateUi(self)

        for i in range(self.ui.keyboard_list.count()):
            self.ui.keyboard_list.setItemText(i, _("General", self.ui.keyboard_list.itemData(i)["name"]))
