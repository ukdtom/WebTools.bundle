######################################################################################################################
#	Plex2CSV module unit					
#
#	Author: dane22, a Plex Community member
#
# This module is for constants used by WebTools and it's modules
#
######################################################################################################################

import io, os, json

DEBUGMODE = False
WT_AUTH = True
VERSION = '2.3 DEV'
UAS_URL = 'https://github.com/ukdtom/UAS2Res'
UAS_BRANCH = 'master'
PREFIX = '/applications/webtools'
NAME = 'WebTools'
ICON = 'WebTools.png'


class consts(object):	
	init_already = False							# Make sure part of init only run once
	# Init of the class
	def __init__(self):
		global DEBUGMODE
		global WT_AUTH
		global UAS_URL
		global UAS_BRANCH
		global VERSION

		# Switch to debug mode if needed
		debugFile = Core.storage.join_path(Core.app_support_path, Core.config.bundles_dir_name, NAME + '.bundle', 'debug')
		# Do we have a debug file ?
		if os.path.isfile(debugFile):
			DEBUGMODE = True
			VERSION = VERSION + ' ****** WARNING Debug mode on *********'
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
		else:
			DEBUGMODE = False

consts = consts()


