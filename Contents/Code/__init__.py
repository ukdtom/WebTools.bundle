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
PREFIX = '/applications/webtools'

NAME = 'WebTools'
ICON = 'WebTools.png'
VERSION = '2.1'
AUTHTOKEN = ''
SECRETKEY = ''


#********** Imports needed *********
import os, io, time
from subprocess import call
from webSrv import startWeb, stopWeb
from random import randint
import uuid			#Used for secrectKey


import datetime

#********** Initialize *********
def Start():
	global SECRETKEY
	PLUGIN_VERSION = VERSION	
	print("********  Started %s on %s  **********" %(NAME  + ' V' + PLUGIN_VERSION, Platform.OS))
	Log.Debug("*******  Started %s on %s  ***********" %(NAME + ' V' + PLUGIN_VERSION, Platform.OS))
	HTTP.CacheTime = 0
	DirectoryObject.thumb = R(ICON)
	ObjectContainer.title1 = NAME + ' V' + PLUGIN_VERSION 
	Plugin.AddViewGroup('List', viewMode='List', mediaType='items')
	ObjectContainer.view_group = 'List'
	makeSettings()

	# Get the secret key used to access the PMS framework ********** FUTURE USE ***************
	SECRETKEY = genSecretKeyAsStr()
	startWeb(SECRETKEY)

####################################################################################################
# Generate secret key
####################################################################################################
''' This will generate the secret key, used to access the framework '''
@route(PREFIX + '/genSecretKeyAsStr')
def genSecretKeyAsStr():
	return str(uuid.uuid4())

####################################################################################################
# Make Settings file
####################################################################################################
''' This will generate the default settings in the Dict if missing '''
@route(PREFIX + '/makeSettings')
def makeSettings():
	Dict['SharedSecret'] = VERSION + '.' + str(randint(0,9999))
	# Set default value for http part, if run for the first time
	if Dict['options_hide_integrated'] == None:
		Dict['options_hide_integrated'] = 'false'
	# Set default value for http part, if run for the first time
	if Dict['options_hide_local'] == None:
		Dict['options_hide_local'] = 'false'
	# Set default value for http part, if run for the first time
	if Dict['options_hide_empty_subtitles'] == None:
		Dict['options_hide_empty_subtitles'] = 'false'
	# Set default value for http part, if run for the first time
	if Dict['options_only_multiple'] == None:
		Dict['options_only_multiple'] = 'false'
	# Set default value for http part, if run for the first time
	if Dict['options_auto_select_duplicate'] == None:
		Dict['options_auto_select_duplicate'] = 'false'
	# Set default value for http part, if run for the first time
	if Dict['items_per_page'] == None:
		Dict['items_per_page'] = '15'
	# Create the password entry
	if Dict['password'] == None:
		Dict['password'] = ''
	# Create the debug entry
	if Dict['debug'] == None:
		Dict['debug'] = 'false'
	# Create the pwdset entry
	if Dict['pwdset'] == None:
		Dict['pwdset'] = False
	return

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
		oc.add(DirectoryObject(key=Callback(MainMenu), title='https://' + Network.Address + ':' + Prefs['WEB_Port_https']))
	else:
		oc.add(DirectoryObject(key=Callback(MainMenu), title='http://' + Network.Address + ':' + Prefs['WEB_Port_http']))
		oc.add(DirectoryObject(key=Callback(MainMenu), title='https://' + Network.Address + ':' + Prefs['WEB_Port_https']))
	oc.add(PrefsObject(title='Preferences', thumb=R('icon-prefs.png')))
	Log.Debug("**********  Ending MainMenu  **********")
	return oc
	
####################################################################################################
# ValidatePrefs
####################################################################################################
@route(PREFIX + '/ValidatePrefs')
def ValidatePrefs():
#	HTTP.Request('http://127.0.0.1:32400/:/plugins/com.plexapp.plugins.WebTool/restart', immediate=True)
	Restart()

@route(PREFIX + '/Restart')
def Restart():
	time.sleep(3)
	startWeb(SECRETKEY)
	return

