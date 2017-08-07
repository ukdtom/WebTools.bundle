######################################################################################################################
#	WebTools module unit					
#
#	Author: dane22, a Plex Community member
#
# This module is for constants used by WebTools and it's modules, as well as to control developer mode
#
# For info about the debug file, see the docs
######################################################################################################################

import io, os, json, inspect
from random import randint   #Used for Cookie generation

DEBUGMODE = False																			# default for debug mode
WT_AUTH = True																				# validate password
VERSION = 'ERROR'																			# version of plugin
UAS_URL = 'https://github.com/ukdtom/UAS2Res'												# USA2 Repo branch
UAS_BRANCH = 'master'																		# UAS2 branch to check
PREFIX = ''																					# Prefix
NAME = ''																					# Name of plugin
ICON = 'WebTools.png'																		# Name of Icon in Resource Dir
BASEURL = ''																				# Base url if behind a proxy
JSONTIMESTAMP = 0																			# timestamp for json export
WTURL = 'https://api.github.com/repos/ukdtom/WebTools.bundle/releases/latest'				# URL to latest WebTools
BUNDLEDIRNAME = ''																			# Name of the bundle dir
V3MODULES = {'WT' : 'wtV3', 'PMS': 'pmsV3', 'LOGS': 'logsV3', 'LANGUAGE': 'languageV3', 
			'SETTINGS': 'settingsV3', 'GIT': 'gitV3', 'FINDMEDIA': 'findMediaV3', 'JSONEXPORTER': 'jsonExporterV3', 'PLAYLISTS': 'playlistsV3'}
UILANGUAGE = 'en'
UILANGUAGEDEBUG = False

class consts(object):	
	init_already = False							# Make sure part of init only run once
	# Init of the class
	def __init__(self):
		global DEBUGMODE
		global WT_AUTH
		global UAS_URL
		global UAS_BRANCH
		global VERSION
		global JSONTIMESTAMP
		global BUNDLEDIRNAME
		global NAME
		global PREFIX
		global BASEURL
		global UILANGUAGE
		global UILANGUAGEDEBUG

		self.makeDefaultSettings()

		# Lets find the name of the bundle directory
		BUNDLEDIRNAME = os.path.split(os.path.split(os.path.split(os.path.dirname(os.path.abspath(inspect.stack()[0][1])))[0])[0])[1]
		# Name of this plugin
		NAME = os.path.splitext(BUNDLEDIRNAME)[0]
		# Prefix
		PREFIX = '/applications/' + str(NAME).lower()
		if Prefs['Base_URL'] != None:
			BASEURL = Prefs['Base_URL']
		if not BASEURL.startswith('/'):
			BASEURL = '/' + BASEURL
		if BASEURL.endswith('/'):
			BASEURL = BASEURL[:-1]
		# Grap version number from the version file
		try:			
			versionFile = Core.storage.join_path(Core.bundle_path, 'VERSION')
			with io.open(versionFile, "rb") as version_file:
				VERSION = version_file.read().splitlines()[0]								
		except:
			if not self.isCorrectPath():				
				VERSION = '*** WRONG INSTALL PATH!!!!....Correct path is: ' + Core.storage.join_path(Core.bundle_path, BUNDLEDIRNAME) + '***'
		# Switch to debug mode if needed		
		debugFile = Core.storage.join_path(Core.bundle_path, 'debug')
		# Do we have a debug file ?
		if os.path.isfile(debugFile):
			DEBUGMODE = True
			VERSION = VERSION + ' ****** WARNING Debug mode on *********'
			try:
				# Read it for params
				json_file = io.open(debugFile, "rb")
				debug = json_file.read()
				json_file.close()
				debugParams = JSON.ObjectFromString(str(debug))				
				Log.Debug('Override debug params are %s' %str(debugParams))
				if 'UAS_Repo' in debugParams:
					UAS_URL = debugParams['UAS_Repo']
				if 'UAS_RepoBranch' in debugParams:
					UAS_BRANCH = debugParams['UAS_RepoBranch']
				if 'WT_AUTH' in debugParams:
					WT_AUTH = debugParams['WT_AUTH']
				if 'JSONTIMESTAMP' in debugParams:
					JSONTIMESTAMP = debugParams['JSONTIMESTAMP']
				# Try and fetch a user language, if set
				try:
					UILANGUAGE = Dict['UILanguage']
				except:
					pass
				# Running localization in debug mode?
				if 'UI' in debugParams:					
					if 'Language' in debugParams['UI']:
						UILANGUAGE = debugParams['UI']['Language']						
					if 'debug' in debugParams['UI']:
						UILANGUAGEDEBUG = (debugParams['UI']['debug'] == True)											
			except Exception, e:				
				Log.Exception('Exception in const was %s' %(str(e)))
				pass
			Log.Debug('******** Using the following debug params ***********')
			Log.Debug('DEBUGMODE: ' + str(DEBUGMODE))
			Log.Debug('UAS_Repo: ' + UAS_URL)
			Log.Debug('UAS_RepoBranch: ' + UAS_BRANCH)
			Log.Debug('Authenticate: ' + str(WT_AUTH))
			Log.Debug('JSON timestamp: ' + str(JSONTIMESTAMP))
			Log.Debug('UI Language: ' + str(UILANGUAGE))
			Log.Debug('UI Language Debug: ' + str(UILANGUAGEDEBUG))
			Log.Debug('*****************************************************')
		else:
			DEBUGMODE = False		

		# Verify install path
		def isCorrectPath(self):						
			try:				
				installedPlugInPath = abspath(getsourcefile(lambda:0)).upper().split(BUNDLEDIRNAME,1)[0]
				targetPath = Core.storage.join_path(Core.app_support_path, Core.config.bundles_dir_name).upper()
				if installedPlugInPath[:-1] != targetPath:
					Log.Debug('************************************************')
					Log.Debug('Wrong installation path detected!!!!')
					Log.Debug('')
					Log.Debug('Correct path is:')
					Log.Debug(Core.storage.join_path(Core.app_support_path, Core.config.bundles_dir_name, BUNDLEDIRNAME))
					Log.Debug('************************************************')
					installedPlugInPath = abspath(getsourcefile(lambda:0)).split('/Contents',1)[0]
					return False
				else:
					Log.Info('Verified a correct install path as: ' + targetPath)
					return True
			except Exception, e:
				Log.Exception('Exception in IsCorrectPath was: %s' %str(e))				

####################################################################################################
# Make default Dict
####################################################################################################
	''' This will generate the default settings in the Dict if missing '''
	def makeDefaultSettings(self):
		# Used for Cookie generation
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
		# Init the installed dict
		if Dict['installed'] == None:
			Dict['installed'] = {}
		# Init the allBundle Dict
		if Dict['PMS-AllBundleInfo'] == None:
			Dict['PMS-AllBundleInfo'] = {}
		# Init the scheme used Dict
		if Dict['wt_csstheme'] == None:
			Dict['wt_csstheme'] = 'WhiteBlue.css'
		# Init default language to en, if none is present
		if Dict['UILanguage'] == None:
			Dict['UILanguage'] = 'en'
		return

consts = consts()

