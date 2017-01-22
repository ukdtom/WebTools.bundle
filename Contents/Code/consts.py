######################################################################################################################
#	WebTools module unit					
#
#	Author: dane22, a Plex Community member
#
# This module is for constants used by WebTools and it's modules, as well as to control developer mode
#
# For info about the debug file, see the docs
######################################################################################################################

import io, os, json

DEBUGMODE = False																	# default for debug mode
WT_AUTH = True																		# validate password
VERSION = 'ERROR'																	# version of WebTools
UAS_URL = 'https://github.com/ukdtom/UAS2Res'			# USA2 Repo branch
UAS_BRANCH = 'master'															# UAS2 branch to check
PREFIX = '/applications/webtools'
NAME = 'WebTools'
ICON = 'WebTools.png'
JSONTIMESTAMP = 0																	# timestamp for json export
WTURL = 'https://api.github.com/repos/ukdtom/WebTools.bundle/releases/latest'				# URL to latest WebTools


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

		# Grap version number from the version file
		try:
			versionFile = Core.storage.join_path(Core.app_support_path, Core.config.bundles_dir_name, NAME + '.bundle', 'VERSION')
			with io.open(versionFile, "rb") as version_file:
				VERSION = version_file.read().splitlines()[0]								
		except:
			if not self.isCorrectPath():
				VERSION = '*** WRONG INSTALL PATH!!!!....Correct path is: ' + Core.storage.join_path(Core.app_support_path, Core.config.bundles_dir_name, NAME + '.bundle' + '***')

		# Switch to debug mode if needed
		debugFile = Core.storage.join_path(Core.app_support_path, Core.config.bundles_dir_name, NAME + '.bundle', 'debug')
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
			except:
				pass
			Log.Debug('******** Using the following debug params ***********')
			Log.Debug('DEBUGMODE: ' + str(DEBUGMODE))
			Log.Debug('UAS_Repo: ' + UAS_URL)
			Log.Debug('UAS_RepoBranch: ' + UAS_BRANCH)
			Log.Debug('Authenticate: ' + str(WT_AUTH))
			Log.Debug('JSON timestamp: ' + str(JSONTIMESTAMP))
			Log.Debug('*****************************************************')
		else:
			DEBUGMODE = False

		# Verify install path
		def isCorrectPath(self):	
			installedPlugInPath, skipStr = abspath(getsourcefile(lambda:0)).upper().split(str(NAME).upper() + '.BUNDLE',1)
			targetPath = Core.storage.join_path(Core.app_support_path, Core.config.bundles_dir_name).upper()
			if installedPlugInPath[:-1] != targetPath:
				Log.Debug('************************************************')
				Log.Debug('Wrong installation path detected!!!!')
				Log.Debug('')
				Log.Debug('Correct path is:')
				Log.Debug(Core.storage.join_path(Core.app_support_path, Core.config.bundles_dir_name, NAME + '.bundle'))
				Log.Debug('************************************************')
				installedPlugInPath, skipStr = abspath(getsourcefile(lambda:0)).split('/Contents',1)
				return False
			else:
				Log.Info('Verified a correct install path as: ' + targetPath)
				return True



consts = consts()


