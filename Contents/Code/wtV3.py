######################################################################################################################
#	WT unit				
# A WebTools bundle plugin	
#
# Used for internal functions to WebTools
#
#	Author: dane22, a Plex Community member
#
######################################################################################################################

import glob
import json
import shutil, sys, os
from consts import BUNDLEDIRNAME, NAME, VERSION
from plextvhelper import plexTV
from shutil import copyfile

GET = ['GETCSS', 'GETUSERS', 'GETLANGUAGELIST']
PUT = ['RESET']
POST = ['']
DELETE = ['']

PAYLOAD = 'aWQ9MTE5Mjk1JmFwaV90b2tlbj0wODA2OGU0ZjRkNTI3NDVlOTM0NzAyMWQ2NDU5MGYzOQ__'
TRANSLATESITEBASE = 'https://api.poeditor.com/v2'
TRANSLATESITEHEADER = {'content-type': 'application/x-www-form-urlencoded'}


class wtV3(object):	

	@classmethod
	def init(self):
		return

	''' Get the relevant function and call it with optinal params '''
	@classmethod
	def getFunction(self, metode, req):		
		self.init()
		params = req.request.uri[8:].upper().split('/')		
		self.function = None
		if metode == 'get':
			for param in params:
				if param in GET:
					self.function = param
					break
				else:
					pass
		elif metode == 'post':
			for param in params:
				if param in POST:
					self.function = param
					break
				else:
					pass
		elif metode == 'put':
			for param in params:
				if param in PUT:
					self.function = param
					break
				else:
					pass
		elif metode == 'delete':
			for param in params:
				if param in DELETE:
					self.function = param
					break
				else:
					pass
		if self.function == None:
			Log.Debug('Function to call is None')
			req.clear()
			req.set_status(404)
			req.finish('Unknown function call')
		else:		
			# Check for optional argument
			paramsStr = req.request.uri[req.request.uri.upper().find(self.function) + len(self.function):]			
			# remove starting and ending slash
			if paramsStr.endswith('/'):
				paramsStr = paramsStr[:-1]
			if paramsStr.startswith('/'):
				paramsStr = paramsStr[1:]
			# Turn into a list
			params = paramsStr.split('/')
			# If empty list, turn into None
			if params[0] == '':
				params = None
			try:
				Log.Debug('Function to call is: ' + self.function + ' with params: ' + str(params))
				if params == None:
					getattr(self, self.function)(req)
				else:
					getattr(self, self.function)(req, params)
			except Exception, e:
				Log.Exception('Exception in process of: ' + str(e))

	#********** Functions below ******************

	# Get list of avail languages, as well as their translation status
	@classmethod
	def GETLANGUAGELIST(self, req, *args):
		try:				
			response = HTTP.Request(method = 'POST', url = TRANSLATESITEBASE + '/languages/list', data=String.Decode(PAYLOAD), headers=TRANSLATESITEHEADER)			
			jsonResponse = JSON.ObjectFromString(str(response))						
			req.set_status(200)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish(json.dumps(jsonResponse['result']['languages']))
		except Exception, e:
			Log.Exception('Exception happened in getLanguageList was: ' + str(e))
			req.clear()
			req.set_status(500)			
			req.finish('Fatal error happened in wt.getLanguageList: %s' %(str(e)))

	# Get list of users
	@classmethod
	def GETUSERS(self, req, *args):
		try:
			users = plexTV().getUserList()
			req.clear()
			if users == None:
				req.set_status(401)
			else:
				req.set_status(200)
				req.set_header('Content-Type', 'application/json; charset=utf-8')
				req.finish(json.dumps(users))
		except Exception, e:
			Log.Exception('Fatal error happened in wt.getUsers: ' + str(e))
			req.clear()
			req.set_status(500)			
			req.finish('Fatal error happened in wt.getUsers: %s' %(str(e)))


	# Reset WT to factory settings
	@classmethod
	def RESET(self, req, *args):
		try:
			Log.Info('Factory Reset called')
			cachePath = Core.storage.join_path(Core.app_support_path, 'Plug-in Support', 'Caches', 'com.plexapp.plugins.' + NAME)
#			dataPath = Core.storage.join_path(Core.app_support_path, 'Plug-in Support', 'Data', 'com.plexapp.plugins.' + NAME) 
			shutil.rmtree(cachePath)
			try:
				Dict.Reset()
			except:
				Log.Critical('Fatal error in clearing dict during reset')
			# Restart system bundle
			HTTP.Request('http://127.0.0.1:32400/:/plugins/com.plexapp.plugins.' + NAME + '/restart', cacheTime=0, immediate=True)
			req.clear()
			req.set_status(200)
			req.finish('WebTools has been reset')
		except Exception, e:
			Log.Exception('Fatal error happened in wt.reset: ' + str(e))
			req.clear()
			req.set_status(500)			
			req.finish('Fatal error happened in wt.reset: %s' %(str(e)))

	# Get a list of all css files in http/custom_themes
	@classmethod
	def GETCSS(self,req, *args):			
		Log.Debug('getCSS requested')
		try:
			targetDir = Core.storage.join_path(Core.app_support_path, Core.config.bundles_dir_name, BUNDLEDIRNAME, 'http', 'custom_themes')
			myList = glob.glob(targetDir + '/*.css')
			if len(myList) == 0:
				req.clear()
				req.set_status(204)
			else:
				for n,item in enumerate(myList):
					myList[n] = item.replace(targetDir,'')
					myList[n] = myList[n][1:]
				Log.Debug('Returning %s' %(myList))
				req.clear()
				req.set_status(200)
				req.set_header('Content-Type', 'application/json; charset=utf-8')
				req.finish(json.dumps(myList))
		except Exception, e:
			Log.Exception('Fatal error happened in getCSS: ' + str(e))
			req.clear()
			req.set_status(500)
			req.finish('Fatal error happened in getCSS: ' + str(e))

#********************* Internal functions ***********************************

# This function will do a cleanup of old stuff, if needed
def upgradeCleanup():
	# Always check translation file regardless of version
	updateTranslationStore()
	'''
	We do take precedence here in a max of 3 integer digits in the version number !
	'''
	Log.Info('Running upgradeCleanup')
	versionArray = VERSION.split('.')
	try:
		major = int(versionArray[0])
	except Exception, e:
		Log.Exception('Exception happened digesting the major number of the Version was %s' %(str(e)))
	try:
		minor = int(versionArray[1])
	except Exception, e:
		Log.Exception('Exception happened digesting the minor number of the Version was %s' %(str(e)))
	try:
		# When getting rev number, we need to filter out stuff like dev version
		rev = int(versionArray[2].split(' ')[0])
	except Exception, e:
		Log.Exception('Exception happened digesting the rev number of the Version was %s' %(str(e)))
	# Older than V3 ?
	if major > 2:
		# We need to delete the old uas dir, if present
		dirUAS = Core.storage.join_path(Core.app_support_path, Core.config.bundles_dir_name, NAME + '.bundle', 'http', 'uas')
		try:
			if os.path.isdir(dirUAS):
				Log.Debug('Found old uas V2 cache dir, so deleting that')
				shutil.rmtree(dirUAS)				
		except Exception, e:
			Log.Exception('We encountered an error during cleanup that was %s' %(str(e)))
			pass
			
# This function will update the translation.js file if needed
def updateTranslationStore():	
	bundleStore = Core.storage.join_path(Core.bundle_path, 'http', 'static', '_shared', 'translations.js')
	dataStore = Core.storage.join_path(Core.app_support_path, 'Plug-in Support', 'Data', 'com.plexapp.plugins.WebTools', 'DataItems', 'translations.js')	
	#If translations.js file already present in the store, we need to find out if it's newer or not
	if Data.Exists('translations.js'):
		# File exsisted, so let's compare datetime stamps
		dataStore_modified_time = os.stat(dataStore).st_mtime
		bundleStore_modified_time = os.stat(bundleStore).st_mtime		
		if dataStore_modified_time < bundleStore_modified_time:			
			Log.Info('Updating translation file in storage')
			copyfile(bundleStore, dataStore)
	else:
		Log.Info('Updating translation file in storage')
		copyfile(bundleStore, dataStore)
	return