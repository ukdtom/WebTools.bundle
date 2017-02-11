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
import shutil, sys
from consts import BUNDLEDIRNAME, NAME

GET = ['GETCSS']
PUT = ['RESET']
POST = ['']
DELETE = ['']


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
			req.set_status(412)
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

	# Reset WT to factory settings
	@classmethod
	def RESET(self, req):
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
	def GETCSS(self,req):			
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

