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

class wt(object):	

	''' Grap the tornado req, and process it '''
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
					myList[n] = item.replace(targetDir + '/','')
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

				
	
