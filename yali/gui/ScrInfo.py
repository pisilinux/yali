# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#
import os
try:
    from PyQt5.QtCore import QCoreApplication
    _ = QCoreApplication.translate
except:
    _ = lambda x,y: y

from PyQt5.QtWidgets import QWidget, qApp
from PyQt5.QtCore import pyqtSignal, QTranslator, QDir, QLocale
import yali.context as ctx
from yali.gui import ScreenWidget
from yali.gui.Ui.info import Ui_InfoWidget

Locale = QLocale


class Widget(QWidget, ScreenWidget):
    name = "info"
    
    if os.path.exists(ctx.consts.lang_path):
        _path = ctx.consts.lang_path
    else:
        _path = "./lang"
    
    lang_dir = QDir(_path)

    def __init__(self):
        QWidget.__init__(self)
        self.ui = Ui_InfoWidget()
        self.ui.setupUi(self)
        
        self.createLangItems()
        self.ui.comboBox.currentIndexChanged[int].connect(self.loadLang)
        
        if ctx.lang in self._locales:
            self.loadLang(lang=ctx.lang)
        else:
            self.loadLang()
            
    def createLangItems(self):
        fileNames = self.lang_dir.entryList(["*.qm"])
        self._locales = []
        for i in fileNames:
            locale = i.split(".")[0]
            self.ui.comboBox.addItem(
                Locale.nativeLanguageName(Locale(locale)),
                locale
                )
            #print(Locale.languageToString(Locale(locale).language()))
            self._locales.append(locale)
        i = self.ui.comboBox.findData(ctx.lang)
        if i>0 :
            self.ui.comboBox.setCurrentIndex(i)

    def loadLang(self, index=0, lang=None):
        try:
            qApp.removeTranslator(self.translator)
        except:
            pass

        if not lang:
            if self.ui.comboBox.findData(index) < 0:
                lang = self.ui.comboBox.itemData(index)
            
        ctx.lang = lang
        
        qmFile = os.path.join(str(self._path), "{lang}.qm".format(lang=lang))
        if not os.path.exists(qmFile):
            return
        
        self.translator = QTranslator()

        self.translator.load(qmFile)
        qApp.installTranslator(self.translator)
        self.retranslateUi()
        
        ctx.mainScreen.retranslateUi()
        
        try:
            ctx.mainScreen.stackMove(0)
        except:
            pass
        
        try:
            hata_sayisi = 0
            
            for widget in qApp.allWidgets():
                try:
                    widget.ui.retranslateUi(widget)
                except:
                    pass
        except:
            print("hata ")

    def shown(self):
        ctx.mainScreen.disableBack()
        
    def retranslateUi(self):
        self.ui.retranslateUi(self)
        
        fileNames = self.lang_dir.entryList(["*.qm"])
        
        for i in fileNames:
            locale = i.split(".")[0]
            index = self.ui.comboBox.findData(locale)
            #print(locale, index)
            self.ui.comboBox.setItemText(index, _("General", Locale.languageToString(Locale(locale).language())))
