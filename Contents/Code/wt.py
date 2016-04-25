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
import shutil

class wt(object):	

	''' Grap the tornado get req, and process it '''
	def reqprocess(self, req):	
		function = req.get_argument('function', 'missing')
		if function == 'missing':
			req.clear()
			req.set_status(412)
			req.finish("Missing function parameter")
		elif function == 'getCSS':
			# Call getCSS
			return self.getCSS(req)
		else:
			req.clear()
			req.set_status(412)
			req.finish("Unknown function call")

	''' Grap the tornado req, and process it for a POST request'''
	def reqprocessPost(self, req):		
		function = req.get_argument('function', 'missing')
		if function == 'missing':
			req.clear()
			req.set_status(412)
			req.finish('Missing function parameter')
		elif function == 'reset':
			return self.reset(req)
		else:
			req.clear()
			req.set_status(412)
			req.finish('Unknown function call')

	# Reset WT to factory settings
	def reset(self, req):
		try:
			cachePath = Core.storage.join_path(Core.app_support_path, 'Plug-in Support', 'Caches', 'com.plexapp.plugins.WebTools')
			dataPath = Core.storage.join_path(Core.app_support_path, 'Plug-in Support', 'Data', 'com.plexapp.plugins.WebTools')
			shutil.rmtree(cachePath)
			shutil.rmtree(dataPath)
			# Restart system bundle
			HTTP.Request('http://127.0.0.1:32400/:/plugins/com.plexapp.plugins.WebTools/restart', cacheTime=0, immediate=True)
			req.clear()
			req.set_status(200)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish('WebTools has been reset')
		except Exception, e:
			Log.Debug('Fatal error happened in wt.reset: ' + str(e))
			req.clear()
			req.set_status(500)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish('Fatal error happened in wt.reset: ' + str(e))

	# Get a list of all css files in http/custom_themes
	def getCSS(self,req):
		Log.Debug('getCSS requested')
		try:
			targetDir = Core.storage.join_path(Core.app_support_path, Core.config.bundles_dir_name, 'WebTools.bundle', 'http', 'custom_themes')
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
			Log.Debug('Fatal error happened in getCSS: ' + str(e))
			req.clear()
			req.set_status(500)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish('Fatal error happened in getCSS: ' + str(e))

				
	
