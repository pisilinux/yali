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


locales = {

"tr" : {
        "name" : _("General", "Turkish"),
        "xkblayout" : "tr",
        "xkbvariant" : [["f",_("General", "Turkish F")],["",_("General", "Turkish Q")]],
        "locale" : "tr_TR.UTF-8",
        "consolekeymap" : ["trf","trq"],
        "consolefont" : "iso09.16",
        "consoletranslation" : "8859-9",
        "timezone" : "Europe/Istanbul"
        },

"en" : {
        "name" : _("General", "English"),
        "xkblayout" : "us",
        "xkbvariant" : None,
        "locale" : "en_US.UTF-8",
        "consolekeymap" : "us",
        "consolefont" : "iso01.16",
        "consoletranslation" : "8859-1",
        "timezone" : "America/New_York"
        },

"gb" : {
        "name" : _("General", "English GB"),
        "xkblayout" : "gb",
        "xkbvariant" : None,
        "locale" : "en_GB.UTF-8",
        "consolekeymap" : "uk",
        "consolefont" : "iso01.16",
        "consoletranslation" : "8859-1"
        },

"gr" : {
        "name" : _("General", "Greek"),
        "xkblayout" : "gr",
        "xkbvariant" : None,
        "locale" : "el_GR.UTF-8",
        "consolekeymap" : "gr",
        "consolefont" : None,
        "consoletranslation" : None
        },

"af" : {
        "name" : _("General", "Afrikaans"),
        "xkblayout" : "us",
        "xkbvariant" : None,
        "locale" : "af_ZA.UTF-8",
        "consolekeymap" : "us",
        "consolefont" : None,
        "consoletranslation" : None
        },

"vi" : {
        "name" : _("General", "Vietnamese"),
        "xkblayout" : "vn",
        "xkbvariant" : None,
        "locale" : "vi_VN.UTF-8",
        "consolekeymap" : "us",
        "consolefont" : None,
        "consoletranslation" : None
        },

"ca" : {
        "name" : _("General", "Catalan"),
        "xkblayout" : "es",
        "xkbvariant" : None,
        "locale" : "ca_ES.UTF-8",
        "consolekeymap" : "es",
        "consolefont" : None,
        "consoletranslation" : None,
        "timezone" : "Europe/Madrid"
        },

"it" : {
        "name" : _("General", "Italian"),
        "xkblayout" : "it",
        "xkbvariant" : None,
        "locale" : "it_IT.UTF-8",
        "consolekeymap" : "it",
        "consolefont" : None,
        "consoletranslation" : None,
        "timezone" : "Europe/Rome"
        },

"cz" : {
        "name" : _("General", "Czech"),
        "xkblayout" : "cz",
        "xkbvariant" : None,
        "locale" : "cs_CZ.UTF-8",
        "consolekeymap" : "cz-lat2",
        "consolefont" : None,
        "consoletranslation" : None
        },

"cy" : {
        "name" : _("General", "Welsh"),
        "xkblayout" : "gb",
        "xkbvariant" : None,
        "locale" : "cy_GB.UTF-8",
        "consolekeymap" : "uk",
        "consolefont" : None,
        "consoletranslation" : None
        },

"ar" : {
        "name" : _("General", "Arabic"),
        "xkblayout" : "ara",
        "xkbvariant" : None,
        "locale" : "ar_SA.UTF-8",
        "consolekeymap" : "us",
        "consolefont" : None,
        "consoletranslation" : None
        },

"et" : {
        "name" : _("General", "Estonian"),
        "xkblayout" : "ee",
        "xkbvariant" : None,
        "locale" : "et_EE.UTF-8",
        "consolekeymap" : "et",
        "consolefont" : None,
        "consoletranslation" : None
        },

"es" : {
        "name" : _("General", "Spanish"),
        "xkblayout" : "es",
        "xkbvariant" : None,
        "locale" : "es_ES.UTF-8",
        "consolekeymap" : "es",
        "consolefont" : None,
        "consoletranslation" : None,
        "timezone" : "Europe/Madrid"
        },

"ru" : {
        "name" : _("General", "Russian"),
        "xkblayout" : "ru,us",
        "xkbvariant" : None,
        "locale" : "ru_RU.UTF-8",
        "consolekeymap" : "ru",
        "consolefont" : None,
        "consoletranslation" : None,
        "timezone" : "Europe/Moscow"
        },

"nl" : {
        "name" : _("General", "Dutch"),
        "xkblayout" : "us",
        "xkbvariant" : None,
        "locale" : "nl_NL.UTF-8",
        "consolekeymap" : "us",
        "consolefont" : "iso01.16",
        "consoletranslation" : "8859-1",
        "timezone" : "Europe/Amsterdam"
        },

"pt" : {
        "name" : _("General", "Portuguese"),
        "xkblayout" : "pt",
        "xkbvariant" : None,
        "locale" : "pt_BR.UTF-8",
        "consolekeymap" : "pt-latin1",
        "consolefont" : None,
        "consoletranslation" : None,
        "timezone" : "Europe/Lisbon"
        },

"nb" : {
        "name" : _("General", "Norwegian"),
        "xkblayout" : "no",
        "xkbvariant" : None,
        "locale" : "nb_NO.UTF-8",
        "consolekeymap" : "no",
        "consolefont" : None,
        "consoletranslation" : None
        },

"is" : {
        "name" : _("General", "Icelandic"),
        "xkblayout" : "is",
        "xkbvariant" : None,
        "locale" : "is_IS.UTF-8",
        "consolekeymap" : "is-latin1",
        "consolefont" : None,
        "consoletranslation" : None
        },

"pl" : {
        "name" : _("General", "Polish"),
        "xkblayout" : "pl",
        "xkbvariant" : None,
        "locale" : "pl_PL.UTF-8",
        "consolekeymap" : "pl2",
        "consolefont" : None,
        "consoletranslation" : None,
        "timezone" : "Europe/Warsaw"
        },

"be" : {
        "name" : _("General", "Belgium"),
        "xkblayout" : "be",
        "xkbvariant" : None,
        "locale" : "be_BY.UTF-8",
        "consolekeymap" : "be-latin1",
        "consolefont" : None,
        "consoletranslation" : None
        },

"fr" : {
        "name" : _("General", "French"),
        "xkblayout" : "fr",
        "xkbvariant" : None,
        "locale" : "fr_FR.UTF-8",
        "consolekeymap" : "fr-latin1",
        "consolefont" : None,
        "consoletranslation" : None,
        "timezone" : "Europe/Paris"
        },

"bg" : {
        "name" : _("General", "Bulgarian"),
        "xkblayout" : "bg",
        "xkbvariant" : None,
        "locale" : "bg_BG.UTF-8",
        "consolekeymap" : "bg",
        "consolefont" : None,
        "consoletranslation" : None
        },

"sl" : {
        "name" : _("General", "Slovenian"),
        "xkblayout" : "si",
        "xkbvariant" : None,
        "locale" : "sl_SI.UTF-8",
        "consolekeymap" : "slovene",
        "consolefont" : None,
        "consoletranslation" : None
        },

"hr" : {
        "name" : _("General", "Croatian"),
        "xkblayout" : "hr",
        "xkbvariant" : None,
        "locale" : "hr_HR.UTF-8",
        "consolekeymap" : "croat",
        "consolefont" : None,
        "consoletranslation" : None
        },

"de" : {
        "name" : _("General", "German"),
        "xkblayout" : "de",
        "xkbvariant" : None,
        "locale" : "de_DE.UTF-8",
        "consolekeymap" : "de-latin1-nodeadkeys",
        "consolefont" : "iso01.16",
        "consoletranslation" : "8859-1",
        "timezone" : "Europe/Berlin"
        },

"da" : {
        "name" : _("General", "Danish"),
        "xkblayout" : "dk",
        "xkbvariant" : None,
        "locale" : "da_DK.UTF-8",
        "consolekeymap" : "dk",
        "consolefont" : None,
        "consoletranslation" : None
        },

"br" : {
        "name" : _("General", "Brazilian"),
        "xkblayout" : "br",
        "xkbvariant" : None,
        "locale" : "pt_BR.UTF-8",
        "consolekeymap" : "br-abnt2",
        "consolefont" : None,
        "consoletranslation" : None
        },

"fi" : {
        "name" : _("General", "Finnish"),
        "xkblayout" : "fi",
        "xkbvariant" : None,
        "locale" : "fi_FI.UTF-8",
        "consolekeymap" : "fi",
        "consolefont" : None,
        "consoletranslation" : None
        },

"hu" : {
        "name" : _("General", "Hungarian"),
        "xkblayout" : "hu",
        "xkbvariant" : None,
        "locale" : "hu_HU.UTF-8",
        "consolekeymap" : "hu",
        "consolefont" : None,
        "consoletranslation" : None,
        "timezone" : "Europe/Budapest"
        },

"ja" : {
        "name" : _("General", "Japanese"),
        "xkblayout" : "jp",
        "xkbvariant" : None,
        "locale" : "ja_JP.UTF-8",
        "consolekeymap" : "jp106",
        "consolefont" : None,
        "consoletranslation" : None
        },

"ml" : {
        "name" : _("General", "Malayalam"),
        "xkblayout" : "us",
        "xkbvariant" : None,
        "locale" : "ml_IN.UTF-8",
        "consolekeymap" : "us",
        "consolefont" : None,
        "consoletranslation" : None
        },

"sv" : {
        "name" : _("General", "Swedish"),
        "xkblayout" : "se",
        "xkbvariant" : None,
        "locale" : "sv_SE.UTF-8",
        "consolekeymap" : "sv-latin1",
        "consolefont" : None,
        "consoletranslation" : None,
        "timezone" : "Europe/Stockholm"
        },

"mk" : {
        "name" : _("General", "Macedonian"),
        "xkblayout" : "mk",
        "xkbvariant" : None,
        "locale" : "mk_MK.UTF-8",
        "consolekeymap" : "mk",
        "consolefont" : None,
        "consoletranslation" : None
        },

"sk" : {
        "name" : _("General", "Slovak"),
        "xkblayout" : "sk",
        "xkbvariant" : None,
        "locale" : "sk_SK.UTF-8",
        "consolekeymap" : "sk-qwerty",
        "consolefont" : None,
        "consoletranslation" : None
        },

"uk" : {
        "name" : _("General", "Ukrainian"),
        "xkblayout" : "ua",
        "xkbvariant" : None,
        "locale" : "uk_UA.UTF-8",
        "consolekeymap" : "ua-utf",
        "consolefont" : None,
        "consoletranslation" : None
        },

"sr" : {
        "name" : _("General", "Serbian"),
        "xkblayout" : "rs",
        "xkbvariant" : None,
        "locale" : "sr_CS.UTF-8",
        "consolekeymap" : "sr-cy",
        "consolefont" : None,
        "consoletranslation" : None
        },
}
