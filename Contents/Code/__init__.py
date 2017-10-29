#!/usr/bin/env python
# -*- coding: utf-8 -*-
######################################################################################################################
#					WebTools bundle for Plex
#
#					Allows you to manipulate subtitles on Plex Media Server
#
#					Author:			dane22, a Plex Community member
#
#					Support thread:	http://forums.plex.tv/discussion/288191
#
######################################################################################################################

#********* Constants used **********
SECRETKEY = ''

#********** Imports needed *********
import sys
import locale
from webSrv import startWeb, stopWeb
import uuid  # Used for secrectKey
import time
import socket
from consts import DEBUGMODE, VERSION, NAME, ICON, PREFIX, BASEURL
from wtV3 import upgradeCleanup

''' Translate function override to avoid unicode decoding bug, as well as make it work in the WebClient.
    Code shamelessly stolen from:
    https://bitbucket.org/czukowski/plex-locale-patch
    and altered a bit to make it work for WebTools
    '''


def L(string):
    try:
        # Missing X-Plex-Language?
        if 'X-Plex-Language' not in Request.Headers:
            Request.Headers['X-Plex-Language'] = Request.Headers['Accept-Language']
        # Grap string to return
        local_string = Locale.LocalString(string)
        # Decode it, since we need it to be XML compliant
        return str(local_string).decode()
    except Exception, e:
        Log.Critical('Exception in L was %s' % str(e))
        pass

####################################################################################################
# Initialize
####################################################################################################


def Start():
    global SECRETKEY
    runningLocale = locale.getdefaultlocale()
    if DEBUGMODE:
        try:
            print("********  Started %s on %s at %s with locale set to %s **********" %
                  (NAME + ' V' + VERSION, Platform.OS, time.strftime("%Y-%m-%d %H:%M"), runningLocale))
        except:
            pass
    Log.Debug("*******  Started %s on %s at %s with locale set to %s ***********" %
              (NAME + ' V' + VERSION, Platform.OS, time.strftime("%Y-%m-%d %H:%M"), runningLocale))
    # Do Upgrade stuff if needed
    upgradeCleanup()
    # TODO: Nasty workaround for issue 189
    if (Platform.OS == 'Windows' and locale.getpreferredencoding() == 'cp1251'):
        sys.setdefaultencoding("cp1251")
        Log.Debug("Default set to cp1251")
    HTTP.CacheTime = 0
    DirectoryObject.thumb = R(ICON)
    ObjectContainer.title1 = NAME + ' V' + VERSION
    Plugin.AddViewGroup('List', viewMode='List', mediaType='items')
    ObjectContainer.view_group = 'List'
    # Get the secret key used to access the PMS framework ********** FUTURE USE ***************
    SECRETKEY = genSecretKeyAsStr()
    startWeb(SECRETKEY)


####################################################################################################
# Main function
####################################################################################################
''' Main menu '''


@handler(PREFIX, NAME, ICON)
@route(PREFIX + '/MainMenu')
def MainMenu():
    Log.Debug("**********  Starting MainMenu  **********")
    oc = ObjectContainer()
    Log.Debug('Network Address: ' + str(Network.Address))
    Log.Debug('WebPort http: ' + str(Prefs['WEB_Port_http']))
    Log.Debug('WebPort https: ' + str(Prefs['WEB_Port_https']))
    Log.Debug('BaseURL: ' + str(BASEURL))
    url = 'http://' + str(Network.Address) + ':' + \
        str(Prefs['WEB_Port_http']) + str(BASEURL)
    urlhttps = 'https://' + str(Network.Address) + ':' + \
        str(Prefs['WEB_Port_https']) + str(BASEURL)
    oc.add(DirectoryObject(key=Callback(MainMenu),
                           title=L("To access this channel, type the url's below to a new browser tab")))
    if Prefs['Force_SSL']:
        oc.add(DirectoryObject(key=Callback(MainMenu), title=urlhttps))
    else:
        oc.add(DirectoryObject(key=Callback(MainMenu), title=url))
        oc.add(DirectoryObject(key=Callback(MainMenu), title=urlhttps))
    oc.add(PrefsObject(title='Preferences', thumb=R('icon-prefs.png')))
    Log.Debug("**********  Ending MainMenu  **********")
    return oc


####################################################################################################
# Generate secret key
####################################################################################################
''' This will generate the secret key, used to access the framework '''


@route(PREFIX + '/genSecretKeyAsStr')
def genSecretKeyAsStr():
    return str(uuid.uuid4())

####################################################################################################
# ValidatePrefs
####################################################################################################


@route(PREFIX + '/ValidatePrefs')
def ValidatePrefs():
    #	HTTP.Request('http://127.0.0.1:32400/:/plugins/com.plexapp.plugins.WebTool/restart', immediate=True)
    Restart()

####################################################################################################
# Restart
####################################################################################################


@route(PREFIX + '/Restart')
def Restart():
    time.sleep(3)
    startWeb(SECRETKEY)
    return
