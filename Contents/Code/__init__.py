#!/usr/bin/env python
# -*- coding: utf-8 -*-
##############################################################################
# WebTools bundle for Plex
#
# Allows you to manipulate subtitles on Plex Media Server
#
# Author:			dane22, a Plex Community member
#
# Support thread:	http://forums.plex.tv/discussion/288191
#
##############################################################################

# ********** Imports needed *********
import sys
import locale
from webSrv import startWeb, stopWeb
import uuid  # Used for secrectKey
import time
import socket
from consts import DEBUGMODE, VERSION, NAME, ICON, PREFIX, BASEURL, UILANGUAGE
from wtV3 import upgradeCleanup

# ********* Constants used **********
SECRETKEY = ''

# Translate function override to avoid unicode decoding bug,
# as well as make it work in the WebClient.
# Code shamelessly stolen from:
# https://bitbucket.org/czukowski/plex-locale-patch
# and altered a bit to make it work for WebTools


def logDirInfo():
    '''
    This will log info about
    the owner/group of bundle dir
    '''
    import os
    from pwd import getpwuid
    from grp import getgrgid
    Log.Info('*** User/Group File Info ***')
    Log.Info(
        'User BundleDir: %s' % getpwuid(
            os.stat(Core.bundle_path).st_uid).pw_name)
    Log.Info(
        'Group BundleDir: %s' % getgrgid(
            os.stat(Core.bundle_path).st_gid).gr_name)
    Log.Info(
        'PMS USER: %s' % os.environ['USER'])


def L(string):
    try:
        # Grap string to return
        local_string = Locale.LocalString(string)
        # Decode it, since we need it to be XML compliant
        return str(local_string).decode()
    except Exception, e:
        Log.Critical('Exception in L was %s' % str(e))
        pass


def Start():
    '''
    This is the startup call of the plugin
    '''
    # Set Plugin UI to the language the user wants
    # Note that title of prefs dialog is controlled by PMS :(
    Locale.DefaultLocale = UILANGUAGE

    global SECRETKEY
    runningLocale = locale.getdefaultlocale()
    strLog = ''.join((
        '"*******  Started %s' % (NAME + ' V' + VERSION),
        ' on %s' % Platform.OS,
        ' at %s' % time.strftime("%Y-%m-%d %H:%M"),
        ' with locale set to %s' % str(runningLocale),
        ' and file system encoding is %s' % str(sys.getfilesystemencoding()),
        ' **********'
    ))
    logDirInfo()
    if DEBUGMODE:
        try:
            print strLog
        except:
            pass
    Log.Debug(strLog)
    # Do Upgrade stuff if needed
    upgradeCleanup()
    # TODO: Nasty workaround for Python not picking up file system encodings
    if (
        (
            Platform.OS == 'Windows') and (
                locale.getpreferredencoding() == 'cp1251')):
        reload(sys)
        sys.setdefaultencoding("cp1251")
        Log.Debug("Default set to cp1251")
    if locale.getpreferredencoding() is None:
        Log.Info('No default filesystem encoding detected')
        reload(sys)
        sys.setdefaultencoding('utf-8')
        Log.Info('Setting default to utf-8')

    HTTP.CacheTime = 0
    DirectoryObject.thumb = R(ICON)
    ObjectContainer.title1 = NAME + ' V' + VERSION
    Plugin.AddViewGroup(
        'List',
        viewMode='List',
        mediaType='items')
    ObjectContainer.view_group = 'List'
    # Get the secret key used to access the
    # PMS framework ********** FUTURE USE ***************
    SECRETKEY = genSecretKeyAsStr()
    startWeb(SECRETKEY)


@handler(PREFIX, NAME, ICON)
@route(PREFIX + '/MainMenu')
def MainMenu():
    ''' Main menu '''
    Log.Debug("**********  Starting MainMenu  **********")
    message = L("You need to type the URL in a new browser tab")
    title = L(
        "To access this channel, type the url's below to a new browser tab")
    oc = ObjectContainer(title1=title, no_history=True, message=message)
    Log.Debug('Network Address: ' + str(Network.Address))
    Log.Debug('WebPort http: ' + str(Prefs['WEB_Port_http']))
    Log.Debug('WebPort https: ' + str(Prefs['WEB_Port_https']))
    Log.Debug('BaseURL: ' + str(BASEURL))
    url = 'http://' + str(Network.Address) + ':' + \
        str(Prefs['WEB_Port_http']) + str(BASEURL)
    urlhttps = 'https://' + str(Network.Address) + ':' + \
        str(Prefs['WEB_Port_https']) + str(BASEURL)
    oc.add(DirectoryObject(
        key=Callback(MainMenu),
        title=L(
            "To access this channel, type the url's below to a new browser tab"
            )))
    if Prefs['Force_SSL']:
        oc.add(DirectoryObject(
            key=Callback(MainMenu),
            title=urlhttps))
    else:
        oc.add(DirectoryObject(
            key=Callback(MainMenu),
            title=url))
        oc.add(DirectoryObject(
            key=Callback(MainMenu),
            title=urlhttps))
    oc.add(PrefsObject(title='Preferences', thumb=R('icon-prefs.png')))
    Log.Debug("**********  Ending MainMenu  **********")
    return oc


@route(PREFIX + '/genSecretKeyAsStr')
def genSecretKeyAsStr():
    ''' This will generate the secret key, used to access the framework '''
    return str(uuid.uuid4())


@route(PREFIX + '/ValidatePrefs')
def ValidatePrefs():
    ''' Runs everytime prefs are updated '''
    '''
    HTTP.Request(
        'http://127.0.0.1:32400/:/plugins/com.plexapp.plugins.WebTool/restart',
        immediate=True)
    '''
    Restart()


@route(PREFIX + '/Restart')
def Restart():
    ''' Restart WebTools'''
    time.sleep(3)
    startWeb(SECRETKEY)
    return
