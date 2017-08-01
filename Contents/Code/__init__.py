#!/usr/bin/env python
# -*- coding: utf-8 -*-
######################################################################################################################
#					WebTools bundle for Plex
#
#					Allows you to manipulate subtitles on Plex Media Server
#
#					Author:			dagaluf, a Plex Community member
#					Author:			dane22, a Plex Community member
#
#					Support thread:	https://forums.plex.tv/discussion/126254
#
######################################################################################################################

#********* Constants used **********
SECRETKEY = ''

#********** Imports needed *********
import sys, locale
from webSrv import startWeb, stopWeb
import uuid			#Used for secrectKey
import time
import socket
from consts import DEBUGMODE, VERSION, NAME, ICON, PREFIX, BASEURL
from wtV3 import upgradeCleanup

####################################################################################################
# Initialize
####################################################################################################
def Start():
	global SECRETKEY
	runningLocale = locale.getdefaultlocale()
	if DEBUGMODE:	
		try:	
			print("********  Started %s on %s at %s with locale set to %s **********" %(NAME  + ' V' + VERSION, Platform.OS, time.strftime("%Y-%m-%d %H:%M"), runningLocale))
		except:
			pass
	Log.Debug("*******  Started %s on %s at %s with locale set to %s ***********" %(NAME + ' V' + VERSION, Platform.OS, time.strftime("%Y-%m-%d %H:%M"), runningLocale))
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
	oc.add(DirectoryObject(key=Callback(MainMenu), title="To access this channel, type the url's below to a new browser tab"))
	if Prefs['Force_SSL']:
		oc.add(DirectoryObject(key=Callback(MainMenu), title='https://' + Network.Address + ':' + Prefs['WEB_Port_https'] + BASEURL))
	else:
		oc.add(DirectoryObject(key=Callback(MainMenu), title='http://' + Network.Address + ':' + Prefs['WEB_Port_http'] + BASEURL))
		oc.add(DirectoryObject(key=Callback(MainMenu), title='https://' + Network.Address + ':' + Prefs['WEB_Port_https'] + BASEURL))
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

