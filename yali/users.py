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
# User management module for YALI.

import os
import re
import copy
import string
import yali.context as ctx

# a set of User instances waiting...
# we'll add these users at the last step of the installation.
PENDING_USERS = []

def reset_pending_users():
    global PENDING_USERS
    PENDING_USERS = []

def get_users():
    return map(lambda x: x[0], [line.split(':') for line in open('/etc/passwd', 'r').readlines()])

class User:
    """ User class for adding or editing new users
        to the installed system """
    def __init__(self, username = ''):
        self.username = username
        self.groups = []
        self.realname = ''
        self.passwd = ''
        self.uid = -1
        self.no_password = False

        # KDE AutoLogin Defaults
        self.auto_login_defaults = {
            "kdm": {"AutoLoginAgain":"false",
                    "AutoLoginDelay":"0",
                    "AutoLoginLocked":"false"},
            "sddm": {},
            "lxdm": {},
            "lightdm": {},
            "gdm": {}}

        self.shadow_path = os.path.join(ctx.consts.target_dir, 'etc/shadow')
        self.passwd_path = os.path.join(ctx.consts.target_dir, 'etc/passwd')
        self.group_path  = os.path.join(ctx.consts.target_dir, 'etc/group')

    def exists(self):
        """ Check if the given user exists on system """
        if filter(lambda x: x == self.username, get_users()):
            return True
        return False

    def usernameIsValid(self):
        """ Check if the given username is valid not """
        valid = string.ascii_letters + '_' + string.digits
        name = self.username
        if len(name) == 0 or filter(lambda x: not x in valid, name) or not name[0] in string.ascii_letters:
            return False
        return True

    def realnameIsValid(self):
        """ Check if the given Real Name is valid or not """
        not_allowed_chars = '\n' + ':'
        return '' == filter(lambda r: [x for x in not_allowed_chars if x == r], self.realname)

    # KDE AutoLogin
    # FIXME: diğer dm için düzenlenmeli
    # def setAutoLogin(self, state=True):
    #     """ Sets the KDE's Autologin feature's state """
    #     conf = ""
    #     if ctx.flags.install_type == ctx.STEP_FIRST_BOOT:
    #         conf = os.path.join(ctx.consts.root_dir, 'etc/X11/kdm/kdmrc')
    #     elif ctx.flags.install_type == ctx.STEP_DEFAULT:
    #         conf = os.path.join(ctx.consts.target_dir, 'etc/X11/kdm/kdmrc')
    #
    #     if not os.path.exists(conf):
    #         ctx.logger.debug("setAutoLogin: Failed, kdmrc not found; possibly KDE is not installed !")
    #         return False
    #
    #     # We shouldn't use ConfigParser for changing kdmrc: 1- It removes all useful comments 2- KConfig confuses when it sees assignments including space characters like ' = '
    #     # Bugs: #9144 and #10034
    #
    #
    #     def set_key(section, key, value, rc):
    #         section_escaped = re.escape(section)
    #
    #         if not re.compile('^%s$' % section_escaped, re.MULTILINE).search(kdmrc):
    #             ctx.logger.debug("setAutoLogin: Failed, '%s' section not found in kdmrc." % section)
    #             return False
    #
    #         result = re.compile('^%s=(.*)$' % key, re.MULTILINE)
    #         if result.search(rc):
    #             return result.sub('%s=%s' % (key, value), rc)
    #
    #         result = re.compile('^#%s=(.*)$' % key, re.MULTILINE)
    #         if result.search(rc):
    #             return result.sub('%s=%s' % (key, value), rc)
    #
    #         # If key can not be found, insert key=value right below the section
    #         return re.compile('^%s$' % section_escaped, re.MULTILINE).sub("%s\n%s=%s" % (section, key, value), rc)
    #
    #     kdmrc = open(conf).read()
    #     section = "[X-:0-Core]"
    #
    #     # Get a deep copy of default option dictionary and add AutoLoginEnable and AutoLoginuser options
    #     auto_login_defaults = copy.deepcopy(self.auto_login_defaults)
    #     auto_login_defaults['AutoLoginEnable'] = str(state).lower()
    #     auto_login_defaults['AutoLoginUser'] = self.username
    #
    #     for opt in auto_login_defaults.keys():
    #         kdmrc = set_key(section, opt, auto_login_defaults[opt], kdmrc)
    #         if kdmrc is False:
    #             return False
    #
    #     kdmrcfp = open(conf, 'w')
    #     kdmrcfp.write(kdmrc)
    #     kdmrcfp.close()
    #
    #     return True

    def setAutoLogin(self, state=True):
        """ Sets the DM's Autologin feature's state """
        dm_conf = "etc/X11/kdm/kdmrc"
        dm = "kdm"
        # set dm conf file
        if os.path.exists("/usr/bin/sddm"):
            #22052022 tarihinde değiştirildi
            #dm_conf = "etc/sddm.conf"
            dm_conf = "usr/lib/sddm/sddm.conf.d/sddm.conf"
            dm = "sddm"
        elif os.path.exists("/usr/sbin/lxdm"):
            dm_conf = "etc/lxdm/lxdm.conf"
            dm = "lxdm"
        elif os.path.exists("/usr/bin/lightdm"):
            dm_conf = "etc/lightdm/lightdm.conf"
            dm = "lightdm"
        elif os.path.exists("/usr/sbin/gdm"):
            dm_conf = "etc/gdm/custom.conf"
            dm = "gdm"

        conf = ""
        if ctx.flags.install_type == ctx.STEP_FIRST_BOOT:
            conf = os.path.join(ctx.consts.root_dir, dm_conf)
            target_dir = ctx.consts.root_dir
        elif ctx.flags.install_type == ctx.STEP_DEFAULT:
            conf = os.path.join(ctx.consts.target_dir, dm_conf)
            target_dir = ctx.consts.target_dir

        if not os.path.exists(conf):
            ctx.logger.debug("setAutoLogin: Failed, Display Manager (DM) \
                configuration file not found; possibly DM \
                (sddm or lxdm or etc.) is not installed !")
            return False

        # We shouldn't use ConfigParser for changing kdmrc: 1- It removes all useful comments 2- KConfig confuses when it sees assignments including space characters like ' = '
        # Bugs: #9144 and #10034


        def set_key(section, key, value, rc):
            section_escaped = re.escape(section)

            if not re.compile('^%s$' % section_escaped, re.MULTILINE).search(rc):
                ctx.logger.debug("setAutoLogin: Failed, '%s' section not found \
                                 in DM conf file." % section)
                return False

            result = re.compile('^%s=(.*)$' % key, re.MULTILINE)
            if result.search(rc):
                return result.sub('%s=%s' % (key, value), rc)

            result = re.compile('^#%s=(.*)$' % key, re.MULTILINE)
            if result.search(rc):
                return result.sub('%s=%s' % (key, value), rc)

            # If key can not be found, insert key=value right below the section
            return re.compile('^%s$' % section_escaped, re.MULTILINE).sub("%s\n%s=%s" % (section, key, value), rc)

        dmrc = open(conf).read()
        auto_login_defaults = copy.deepcopy(self.auto_login_defaults[dm])
        if dm == "kdm":
            section = "[X-:0-Core]"
            # Get a deep copy of default option dictionary and add AutoLoginEnable and AutoLoginuser options
            auto_login_defaults['AutoLoginEnable'] = str(state).lower()
            auto_login_defaults['AutoLoginUser'] = self.username
        elif dm == "sddm": # FIXME: plasma için ayarlandı
            section = "[Autologin]"
            auto_login_defaults['User'] = self.username if state else ""
            #22052022 tarihinde değiştirildi
            #auto_login_defaults['Session'] = "plasma.desktop" if state else ""
        elif dm == "lxdm":
            section = "[base]"
            auto_login_defaults['autologin'] = self.username if state else ""
            if os.path.exists("/usr/bin/startlxqt"):
                auto_login_defaults['session'] = "/usr/bin/startlxqt"
            elif os.path.exists("/usr/bin/startxfce4"):
                auto_login_defaults['session'] = "/usr/bin/startxfce4"
            elif os.path.exists("/usr/bin/mate-session"):
                auto_login_defaults['session'] = "/usr/bin/mate-session"
        elif dm == "lightdm":
            section = "[Seat:*]"

            sessions = os.listdir("%s/usr/share/xsessions" % target_dir)
            session = sessions[0].split(".")[0]

            auto_login_defaults['autologin-user'] = self.username if state else "pisi"
            auto_login_defaults['autologin-session'] = session if state else ""
        elif dm == "gdm": # FIXME: gnome4 için ayarlandı
            section = "[daemon]"
            auto_login_defaults['AutomaticLoginEnable'] = str(state)
            auto_login_defaults['AutomaticLogin'] = self.username if state else ""
            #auto_login_defaults['Session'] = "plasma.desktop" if state else ""


        for opt in auto_login_defaults.keys():
            dmrc = set_key(section, opt, auto_login_defaults[opt], dmrc)
            if dmrc is False:
                return False

        dmrcfp = open(conf, 'w')
        dmrcfp.write(dmrc)
        dmrcfp.close()

        return True



NICK_MAP = {
    u"ğ": u"g",
    u"ü": u"u",
    u"Ü": u"u",
    u"ş": u"s",
    u"Ş": u"s",
    u"ı": u"i",
    u"İ": u"i",
    u"ö": u"o",
    u"Ö": u"o",
    u"ç": u"c",
    u"Ç": u"c",
}

def nick_guess(name, nicklist):
    def convert(name):
        text = ""
        for letter in name:
            if letter in string.ascii_letters:
                text += letter
            else:
                letter = NICK_MAP.get(letter, None)
                if letter:
                    text += letter
        return text

    if name == "":
        return ""

    text = unicode(name).lower().split()


    ret = convert(text[0])

    # First guess: name

    # if user has a name pattern like x. y z, then return y.
    # e.g. a. murat eren, s. caglar onur, h. ibrahim gungor :)
    if len(text) > 2 and "." in text[0]:
        ret = convert(text[1])

    if not ret in nicklist:
        return ret

    # Second guess: nsurname
    if len(text) > 1:
        ret = convert(text[0][0]) + convert(text[1])
        if not ret in nicklist:
            return ret

    # Third guess: namesurname
    if len(text) > 1:
        ret = convert(text[0]) + convert(text[1])
        if not ret in nicklist:
            return ret

    # Last guess: nameN
    i = 2
    while True:
        ret = convert(text[0]) + unicode(i)
        if not ret in nicklist:
            return ret
        i += 1
