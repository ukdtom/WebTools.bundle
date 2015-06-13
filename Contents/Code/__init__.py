######################################################################################################################
#					WebTools bundle for Plex
#
#					Allows you to manipulate subtitles on Plex Media Server
#
#					Author:			dagaluf, a Plex Community member
#					Author:			dane22, a Plex Community member
#
#					Support thread:	https://forums.plex.tv/index.php/topic/119940-webtool-subtitle-manager-development/
#
######################################################################################################################

#********* Constants used **********
PREFIX = '/utils/webtools'
NAME = 'WebTools'
ICON = 'WebTools.png'
VERSION = '0.0.0.16'

#********** Imports needed *********
import os, io
from subprocess import call
#import xml.etree.ElementTree as et
from webSrv import startWeb, stopWeb
from random import randint

#********** Initialize *********
def Start():
	PLUGIN_VERSION = VERSION	
	print("********  Started %s on %s  **********" %(NAME  + ' V' + PLUGIN_VERSION, Platform.OS))
	Log.Debug("*******  Started %s on %s  ***********" %(NAME + ' V' + PLUGIN_VERSION, Platform.OS))
	HTTP.CacheTime = 0
	DirectoryObject.thumb = R(ICON)
	ObjectContainer.title1 = NAME + ' V' + PLUGIN_VERSION 
	Plugin.AddViewGroup('List', viewMode='List', mediaType='items')
	ObjectContainer.view_group = 'List'
	makeSettings()
	ValidatePrefs()

####################################################################################################
# Make Settings file
####################################################################################################
''' This will generate a settings.js file on the fly during startup of this channel
Exsisting file will be overwritten if needed '''
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
	# Set default value for http part, if run for the first time
	if Dict['fatal_error'] == None:
		Dict['fatal_error'] = 'false'
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
	oc.add(DirectoryObject(key=Callback(MainMenu), title="To access this channel, go to"))
	oc.add(DirectoryObject(key=Callback(MainMenu), title='http://' + Network.Address + ':' + Prefs['WEB_Port'] + '/index.html'))
	oc.add(PrefsObject(title='Preferences', thumb=R('icon-prefs.png')))
	Log.Debug("**********  Ending MainMenu  **********")
	return oc
	
####################################################################################################
# ValidatePrefs
####################################################################################################
@route(PREFIX + '/ValidatePrefs')
def ValidatePrefs():
	startWeb()
	return

