######################################################################################################################
#	pms helper unit				
# A WebTools bundle plugin	
#
#	Author: dane22, a Plex Community member
#
#
######################################################################################################################
import shutil, os
import time, json
import io


# Undate uasTypesCounters
def updateUASTypesCounters():
	try:
		counter = {}
		# Grap a list of all bundles
		bundleList = Dict['PMS-AllBundleInfo']
		for bundle in bundleList:
			for bundleType in bundleList[bundle]['type']:
				if bundleType in counter:
					tCounter = int(counter[bundleType]['total'])
					tCounter += 1
					iCounter = int(counter[bundleType]['installed'])
					if 'date' not in bundleList[bundle]:
						bundleList[bundle]['date'] = ''
					if bundleList[bundle]['date'] != '':
						iCounter += 1
					counter[bundleType] = {'installed': iCounter, 'total' : tCounter}
				else:
					if 'date' not in bundleList[bundle]:
						counter[bundleType] = {'installed': 0, 'total' : 1}
					elif bundleList[bundle]['date'] == '':
						counter[bundleType] = {'installed': 0, 'total' : 1}
					else:
						counter[bundleType] = {'installed': 1, 'total' : 1}
		Dict['uasTypes'] = counter
		Dict.Save()
	except Exception, e:
		print 'Fatal error happened in updateUASTypesCounters: ' + str(e)
		Log.Debug('Fatal error happened in updateUASTypesCounters: ' + str(e))

#TODO fix updateAllBundleInfo
# updateAllBundleInfo
def updateAllBundleInfoFromUAS():
	try:
		# Init the Dict
		if Dict['PMS-AllBundleInfo'] == None:
			Dict['PMS-AllBundleInfo'] = {}
			Dict.Save()
		# start by checking if UAS cache has been populated
		jsonUAS = Core.storage.join_path(Core.app_support_path, Core.config.bundles_dir_name, NAME + '.bundle', 'http', 'uas', 'Resources', 'plugin_details.json')
		if os.path.exists(jsonUAS):
			Log.Debug('UAS was present')
			# Let's open it, and walk the gits one by one
			json_file = io.open(jsonUAS, "rb")
			response = json_file.read()
			json_file.close()
			# Convert to a JSON Object
			gits = JSON.ObjectFromString(str(response))
			for git in gits:
				# Rearrange data
				key = git['repo']
				del git['repo']
				# Check if already present, and if an install date also is there
				if key in Dict['PMS-AllBundleInfo']:
					jsonPMSAllBundleInfo = Dict['PMS-AllBundleInfo'][key]
					if 'date' not in jsonPMSAllBundleInfo:
						git['date'] = ""
				else:
						git['date'] = ""
				# Add/Update our Dict
				Dict['PMS-AllBundleInfo'][key] = git
			Dict.Save()
			updateUASTypesCounters()
		else:
			Log.Debug('UAS was sadly not present')
	except Exception, e:
		Log.Debug('Fatal error happened in updateAllBundleInfoFromUAS: ' + str(e))

class pms(object):
	# Defaults used by the rest of the class
	def __init__(self):
		self.LOGDIR = Core.storage.join_path(Core.app_support_path, 'Logs')
		self.PLUGIN_DIR = Core.storage.join_path(Core.app_support_path, Core.config.bundles_dir_name)

	''' Grap the tornado req, and process it for a GET request'''
	def reqprocess(self, req):		
		function = req.get_argument('function', 'missing')
		if function == 'missing':
			req.clear()
			req.set_status(412)
			req.finish("<html><body>Missing function parameter</body></html>")
		elif function == 'getSectionsList':
			return self.getSectionsList(req)
		elif function == 'getSectionSize':
			return self.getSectionSize(req)
		elif function == 'getSection':
			return self.getSection(req)
		elif function == 'getSubtitles':
			return self.getSubtitles(req)
		elif function == 'showSubtitle':
			return self.showSubtitle(req)
		elif function == 'tvShow':
			return self.TVshow(req)
		elif function == 'getAllBundleInfo':
			return self.getAllBundleInfo(req)
		elif function == 'getParts':
			return self.getParts(req)
		else:
			req.clear()
			req.set_status(412)
			req.finish("<html><body>Unknown function call</body></html>")

	''' Grap the tornado req, and process it for a DELETE request'''
	def reqprocessDelete(self, req):		
		function = req.get_argument('function', 'missing')
		if function == 'missing':
			req.clear()
			req.set_status(412)
			req.finish("<html><body>Missing function parameter</body></html>")
		elif function == 'delSub':
			return self.delSub(req)
		elif function == 'delBundle':
			return self.delBundle(req)
		else:
			req.clear()
			req.set_status(412)
			req.finish("<html><body>Unknown function call</body></html>")

	''' Grap the tornado req, and process it for a PUT request'''
	def reqprocessPUT(self, req):		
		function = req.get_argument('function', 'missing')
		if function == 'missing':
			req.clear()
			req.set_status(412)
			req.finish("<html><body>Missing function parameter</body></html>")
		else:
			req.clear()
			req.set_status(412)
			req.finish("<html><body>Unknown function call</body></html>")

	''' Grap the tornado req, and process it for a POST request'''
	def reqprocessPost(self, req):		
		function = req.get_argument('function', 'missing')
		if function == 'missing':
			req.clear()
			req.set_status(412)
			req.finish("<html><body>Missing function parameter</body></html>")
		elif function == 'uploadFile':
			return self.uploadFile(req)
		else:
			req.clear()
			req.set_status(412)
			req.finish("<html><body>Unknown function call</body></html>")

	# getParts
	def getParts(self, req):
		Log.Debug('Got a call for getParts')
		try:
			key = req.get_argument('key', 'missing')
			if key == 'missing':
				req.clear()
				req.set_status(412)
				req.finish("<html><body>Missing key parameter</body></html>")
			try:
				partsUrl = 'http://127.0.0.1:32400/library/metadata/' + key
				partsInfo = {}
				parts = XML.ElementFromURL(partsUrl).xpath('//Part')
				for part in parts:
					partsInfo[part.get('id')] = part.get('file')		
				Log.Debug('Returning: ' + json.dumps(partsInfo))
				req.set_status(200)
				req.set_header('Content-Type', 'application/json; charset=utf-8')
				req.finish(json.dumps(partsInfo))
			except Ex.HTTPError, e:
				self.clear()
				self.set_status(e.code)
				self.finish(e)
		except Exception, e:
			Log.Debug('Fatal error happened in getParts: ' + str(e))
			req.clear()
			req.set_status(500)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish('Fatal error happened in getParts: ' + str(e))

	# uploadFile
	def uploadFile(self, req):
		Log.Debug('Got a call for uploadFile')
		try:
			# Target filename present?
			remoteFile = req.get_argument('remoteFile', 'missing')
			if remoteFile == 'missing':
				req.clear()
				req.set_status(412)
				req.finish("<html><body>Missing remoteFile parameter</body></html>")
			# Upload file present?
			if not 'localFile' in req.request.files:
				req.clear()
				req.set_status(412)
				req.finish("<html><body>Missing upload file parameter named localFile</body></html>")
			# Grap the upload file			
			localFile = req.request.files['localFile'][0]
			# Save it
			output_file = io.open(remoteFile, 'wb')
			output_file.write(localFile['body'])
			output_file.close
			req.clear()
			req.set_status(200)
			req.finish("<html><body>Upload ok</body></html>")
		except Exception, e:
			Log.Debug('Fatal error happened in uploadFile: ' + str(e))
			req.clear()
			req.set_status(500)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish('Fatal error happened in uploadFile: ' + str(e))

	# getAllBundleInfo
	def getAllBundleInfo(self, req):
		Log.Debug('Got a call for getAllBundleInfo')
		try:
			req.clear()
			if Dict['PMS-AllBundleInfo'] == None:
				Log.Debug('getAllBundleInfo has not been populated yet')
				req.set_status(204)
				req.finish('getAllBundleInfo has not been populated yet')
			else:
				Log.Debug('Returning: ' + str(len(Dict['PMS-AllBundleInfo'])) + ' items')
				req.set_status(200)
				req.set_header('Content-Type', 'application/json; charset=utf-8')
				req.finish(json.dumps(Dict['PMS-AllBundleInfo']))
		except Exception, e:
			Log.Debug('Fatal error happened in getAllBundleInfo: ' + str(e))
			req.clear()
			req.set_status(500)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish('Fatal error happened in getAllBundleInfo' + str(e))

	# Delete Bundle
	def delBundle(self, req):
		Log.Debug('Delete bundle requested')
		def removeBundle(bundleName, bundleIdentifier, url):
			try:				
				bundleDataDir = Core.storage.join_path(Core.app_support_path, 'Plug-in Support', 'Data', bundleIdentifier)
				bundleCacheDir = Core.storage.join_path(Core.app_support_path, 'Plug-in Support', 'Caches', bundleIdentifier)
				bundlePrefsFile = Core.storage.join_path(Core.app_support_path, 'Plug-in Support', 'Preferences', bundleIdentifier + '.xml')
				try:
					# Find the bundle directory, regarding of the case used
					dirs = os.listdir(self.PLUGIN_DIR)
					for pluginDir in dirs:
						if pluginDir.endswith('.bundle'):
							# It's a bundle
							if pluginDir.upper() == bundleName.upper():
								bundleInstallDir = Core.storage.join_path(Core.app_support_path, Core.config.bundles_dir_name, pluginDir)
					Log.Debug('Bundle directory name digested as: %s' %(bundleInstallDir))
					shutil.rmtree(bundleInstallDir)
				except:
					Log.Debug("Unable to remove the bundle directory.")
					req.clear()
					req.set_status(500)
					req.set_header('Content-Type', 'application/json; charset=utf-8')
					req.finish('Fatal error happened when trying to remove the bundle directory.')
				try:
					shutil.rmtree(bundleDataDir)
				except:
					Log.Debug("Unable to remove the bundle data directory.")
					Log.Debug("This can be caused by bundle data directory was never generated")
					Log.Debug("Ignoring this")
				try:
					shutil.rmtree(bundleCacheDir)
				except:
					Log.Debug("Unable to remove the bundle cache directory.")
					Log.Debug("This can be caused by bundle data directory was never generated")
					Log.Debug("Ignoring this")
				try:
					os.remove(bundlePrefsFile)
				except:
					Log.Debug("Unable to remove the bundle preferences file.")
					Log.Debug("This can be caused by bundle prefs was never generated")
					Log.Debug("Ignoring this")
				# Remove entry from list dict
				Dict['installed'].pop(url, None)
				# remove entry from PMS-AllBundleInfo dict
				if url.startswith('https://'):
					# UAS bundle, so only nuke date field
					git = Dict['PMS-AllBundleInfo'][url]
					git['date'] = ''
					Dict['PMS-AllBundleInfo'][url] = git
					Dict.Save()
				else:
					# Manual install or migrated, so nuke the entire key
					Dict['PMS-AllBundleInfo'].pop(url, None)
				updateUASTypesCounters()

# TODO
				try:
					Log.Debug('Remider to self...TODO....Restart of System Bundle hangs :-(')
#					HTTP.Request('http://127.0.0.1:32400/:/plugins/com.plexapp.system/restart', immediate=True)
				except:
					Log.Debug("Unable to restart System.bundle. Channel may not vanish without PMS restart.")
					req.clear()
					req.set_status(500)
					req.set_header('Content-Type', 'application/json; charset=utf-8')
					req.finish('Fatal error happened when trying to restart the system.bundle')
			except Exception, e:
				Log.Debug('Fatal error happened in removeBundle: ' + str(e))
				req.clear()
				req.set_status(500)
				req.set_header('Content-Type', 'application/json; charset=utf-8')
				req.finish('Fatal error happened in removeBundle' + str(e))

		# Main function
		try:
			# Start by checking if we got what it takes ;-)
			bundleName = req.get_argument('bundleName', 'missing')
			if bundleName == 'missing':
				req.clear()
				req.set_status(412)
				req.finish("<html><body>Missing bundleName</body></html>")
				return req
			installedBundles = Dict['installed']
			bFoundBundle = False
			for installedBundle in installedBundles:
				if installedBundles[installedBundle]['bundle'].upper() == bundleName.upper():
					removeBundle(bundleName, installedBundles[installedBundle]['identifier'], installedBundle)
					bFoundBundle = True
					break
			if not bFoundBundle:
				Log.Debug('Bundle %s was not found' %(bundleName))
				req.clear()
				req.set_status(404)
				req.set_header('Content-Type', 'application/json; charset=utf-8')
				req.finish('Bundle %s was not found' %(bundleName))
			Log.Debug('Bundle %s was removed' %(bundleName))
			req.clear()
			req.set_status(200)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish('Bundle %s was removed' %(bundleName))
		except:
			Log.Debug('Fatal error happened in delBundle')
			req.clear()
			req.set_status(500)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish('Fatal error happened in delBundle')

	# Delete subtitle
	def delSub(self, req):
		Log.Debug('Delete subtitle requested')
		try:
			# Start by checking if we got what it takes ;-)
			key = req.get_argument('key', 'missing')
			if key == 'missing':
				req.clear()
				req.set_status(412)
				req.finish("<html><body>Missing key to media</body></html>")
				return req
			subKey = req.get_argument('subKey', 'missing')
			if subKey == 'missing':
				req.clear()
				req.set_status(412)
				req.finish("<html><body>Missing subKey to subtitle</body></html>")
				return req
			myURL='http://127.0.0.1:32400/library/metadata/' + key + '/tree'
			# Grap the sub
			sub = XML.ElementFromURL(myURL).xpath('//MediaStream[@id=' + subKey + ']')
			if len(sub) > 0:
				# Sub did exists, but does it have an url?
				filePath = sub[0].get('url')							
				if not filePath:
					# Got an embedded sub here
					Log.Debug('Fatal error happened in delSub, subtitle not found')
					req.clear()
					req.set_status(406)
					req.set_header('Content-Type', 'application/json; charset=utf-8')
					req.finish('Hmmm....This is invalid, and most likely due to trying to delete an embedded sub :-)')
				else:
					if filePath.startswith('media://'):
						'''
	Here we look at an agent provided subtitle, so this part of the function 
	has been crippled on purpose
						'''
						filePath = filePath.replace('media:/', os.path.join(Core.app_support_path, 'Media', 'localhost'))
						# Subtitle name
						agent, sub = filePath.split('_')
						tmp, agent = agent.split('com.')
						# Agent used
						agent = 'com.' + agent				
						filePath2 = filePath.replace('Contents', 'Subtitle Contributions')
						filePath2, language = filePath2.split('Subtitles')
						language = language[1:3]	
						filePath3 = os.path.join(filePath2[:-1], agent, language, sub)

						''' This is removed from the code, due to the fact, that Plex will re-download right after the deletion

						subtitlesXMLPath, tmp = filePath.split('Contents')
						agentXMLPath = os.path.join(subtitlesXMLPath, 'Contents', 'Subtitle Contributions', agent + '.xml')							
						subtitlesXMLPath = os.path.join(subtitlesXMLPath, 'Contents', 'Subtitles.xml')
						self.DelFromXML(agentXMLPath, 'media', sub)
						self.DelFromXML(subtitlesXMLPath, 'media', sub)
						agentXML = XML.ElementFromURL('"' + agentXMLPath + '"')
						#Let's refresh the media
						url = 'http://127.0.0.1:32400/library/metadata/' + params['param2'] + '/refresh&force=1'
						refresh = HTTP.Request(url, immediate=False)

						# Nuke the actual file
						try:
							# Delete the actual file
							os.remove(filePath)
							print 'Removing: ' + filePath

							os.remove(filePath3)
							print 'Removing: ' + filePath3
							# Refresh the subtitles in Plex
							self.getSubTitles(params)
						except:
							return 500
						'''

						retValues = {}
						retValues['FilePath']=filePath3
						retValues['SymbLink']=filePath

						Log.Debug('Agent subtitle returning %s' %(retValues))
						req.clear()
						req.set_status(200)
						req.set_header('Content-Type', 'application/json; charset=utf-8')
						req.finish(json.dumps(retValues))
						return req
					elif filePath.startswith('file://'):
						# We got a sidecar here, so killing time.....YES

						filePath = filePath.replace('file://', '')
						try:
							# Delete the actual file
							os.remove(filePath)
							retVal = {}
							retVal['Deleted file'] = filePath
							Log.Debug('Deleted the sub %s' %(filePath))
							req.clear()
							req.set_status(200)
							req.set_header('Content-Type', 'application/json; charset=utf-8')
							req.finish(json.dumps(retVal))
						except:
							# Could not find req. subtitle
							Log.Debug('Fatal error happened in delSub, when deleting %s' %(filePath))
							req.clear()
							req.set_status(404)
							req.set_header('Content-Type', 'application/json; charset=utf-8')
							req.finish('Fatal error happened in delSub, when deleting %s' %(filePath))
			else:
				# Could not find req. subtitle
				Log.Debug('Fatal error happened in delSub, subtitle not found')
				req.clear()
				req.set_status(404)
				req.set_header('Content-Type', 'application/json; charset=utf-8')
				req.finish('Could not find req. subtitle')
		except:
			Log.Debug('Fatal error happened in delSub')
			req.clear()
			req.set_status(500)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish('Fatal error happened in delSub')

	''' TVShow '''
	def TVshow(self, req):
		Log.Debug('TV Show requested')

		# Get Season contents
		def getSeason(req, key):
			try:
				bGetSubs = (req.get_argument('getSubs', 'False').upper()=='TRUE')
				Log.Debug('Got a season request')
				myURL = 'http://127.0.0.1:32400/library/metadata/' + key + '/tree'
				episodes = XML.ElementFromURL(myURL).xpath('.//MetadataItem/MetadataItem')
				mySeason = []
				for episode in episodes:
					myEpisode = {}
					myEpisode['key'] = episode.get('id')					
					myEpisode['title'] = episode.get('title')					
					myEpisode['episode'] = episode.get('index')
					if bGetSubs:
						myEpisode['subtitles'] = self.getSubtitles(req, mediaKey=myEpisode['key'])
					mySeason.append(myEpisode)
				Log.Debug('returning: %s' %(mySeason))
				req.clear()
				req.set_status(200)
				req.set_header('Content-Type', 'application/json; charset=utf-8')
				req.finish(json.dumps(mySeason))
			except:
				Log.Debug('Fatal error happened in TV-Show while fetching season')
				req.clear()
				req.set_status(500)
				req.set_header('Content-Type', 'application/json; charset=utf-8')
				req.finish('Fatal error happened in TV-Show while fetching season')


		# Get Seasons list
		def getSeasons(req, key):
			try:
				myURL = 'http://127.0.0.1:32400/library/metadata/' + key + '/children'				
				mySeasons = []
				seasons = XML.ElementFromURL(myURL).xpath('//Directory')
				for season in seasons:
					if season.get('ratingKey'):
						mySeason = {}
						mySeason['title'] = season.get('title')
						mySeason['key'] = season.get('ratingKey')					
						mySeason['season'] = season.get('index')
						mySeason['size'] = season.get('leafCount')					
						mySeasons.append(mySeason)
				Log.Debug('Returning seasons as %s' %(mySeasons))
				req.clear()
				req.set_status(200)
				req.set_header('Content-Type', 'application/json; charset=utf-8')
				req.finish(str(json.dumps(mySeasons)))
			except:
				Log.Debug('Fatal error happened in TV-Show while fetching seasons')
				req.clear()
				req.set_status(500)
				req.set_header('Content-Type', 'application/json; charset=utf-8')
				req.finish('Fatal error happened in TV-Show while fetching seasons')


		# Get Size function
		def getSize(req, key):
			Log.Debug('Get TV-Show Size req. for %s' %(key))
			# Grap TV-Show size
			myURL = 'http://127.0.0.1:32400/library/metadata/' + key + '/allLeaves?X-Plex-Container-Start=0&X-Plex-Container-Size=0'
			try:
				size = XML.ElementFromURL(myURL).get('totalSize')		
				Log.Debug('Returning size as %s' %(size))
				req.clear()
				req.set_status(200)
				req.set_header('Content-Type', 'application/json; charset=utf-8')
				req.finish(size)
			except:
				Log.Debug('Fatal error happened in TV-Show while fetching size')
				req.clear()
				req.set_status(500)
				req.set_header('Content-Type', 'application/json; charset=utf-8')
				req.finish('Fatal error happened in TV-Show while fetching size')

		# Get Contents
		def getContents(req, key):
			try:
				# Start of items to grap
				start = req.get_argument('start', 'missing')
				if start == 'missing':
					req.clear()
					req.set_status(412)
					req.finish('You are missing start param')
					return req
				# Amount of items to grap
				size = req.get_argument('size', 'missing')
				if size == 'missing':
					req.clear()
					req.set_status(412)
					req.finish("You are missing size param")
					return req
				# Get subs info as well ?
				bGetSubs = (req.get_argument('getSubs', 'False').upper()=='TRUE')
				myURL = 'http://127.0.0.1:32400/library/metadata/' + key + '/allLeaves?X-Plex-Container-Start=' + start + '&X-Plex-Container-Size=' + size
				shows = XML.ElementFromURL(myURL).xpath('//Video')
				episodes=[]
				for media in shows:
					episode = {}
					episode['key'] = media.get('ratingKey')
					episode['title'] = media.get('title')
					episode['season'] = media.get('parentIndex')
					episode['episode'] = media.get('index')
					if bGetSubs:
						episode['subtitles'] = self.getSubtitles(req, mediaKey=episode['key'])
					episodes.append(episode)					
				Log.Debug('Returning episodes as %s' %(episodes))
				req.clear()
				req.set_status(200)
				req.set_header('Content-Type', 'application/json; charset=utf-8')
				req.finish(json.dumps(episodes))
			except:
				Log.Debug('Fatal error happened in TV-Show while fetching contents')
				req.clear()
				req.set_status(500)
				req.set_header('Content-Type', 'application/json; charset=utf-8')
				req.finish('Fatal error happened in TV-Show while fetching contents')

		# Main func
		try:
			Log.Debug('Start TV Show')
			key = req.get_argument('key', 'missing')
			Log.Debug('Show key is %s' %(key))
			if key == 'missing':
				req.clear()
				req.set_status(412)
				req.finish('Missing key of Show')
				return req
			action = req.get_argument('action', 'missing')
			Log.Debug('Show action is %s' %(action))
			if action == 'missing':
				req.clear()
				req.set_status(412)
				req.finish('Missing action param of Show')
				return req
			# Let's follow the action here
			if action == 'getSize':
				getSize(req, key)
			elif action == 'getContents':
				getContents(req, key)
			elif action == 'getSeasons':
				getSeasons(req, key)
			elif action == 'getSeason':
				getSeason(req, key)
			else:
				Log.Debug('Unknown action for TVshow')
				req.clear()
				req.set_status(412)
				req.set_header('Content-Type', 'application/json; charset=utf-8')
				req.finish('Unknown action for TVshow')		
		except:
			Log.Debug('Fatal error happened in TVshow')
			req.clear()
			req.set_status(500)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish('Fatal error happened in TVshow')

	''' Show Subtitle '''
	def showSubtitle(self, req):
		Log.Debug('Show Subtitle requested')
		try:
			key = req.get_argument('key', 'missing')
			Log.Debug('Subtitle key is %s' %(key))
			if key == 'missing':
				req.clear()
				req.set_status(412)
				req.finish('Missing key of subtitle')
				return req
			myURL='http://127.0.0.1:32400/library/streams/' + key
			try:
				response = HTML.StringFromElement(HTML.ElementFromURL(myURL))
				response = response.replace('<p>', '',1)
				response = response.replace('</p>', '',1)
				response = response.replace('&gt;', '>')
				response = response.split('\n')
				req.clear()
				req.set_status(200)
				req.set_header('Content-Type', 'application/json; charset=utf-8')
				req.finish(json.dumps(response))
			except:
				Log.Debug('Fatal error happened in showSubtitle')
				req.clear()
				req.set_status(500)
				req.set_header('Content-Type', 'application/json; charset=utf-8')
				req.finish('Fatal error happened in showSubtitle')
		except:
			Log.Debug('Fatal error happened in showSubtitle')
			req.clear()
			req.set_status(500)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish('Fatal error happened in showSubtitle')

	''' get Subtitles '''
	def getSubtitles(self, req, mediaKey=''):
		Log.Debug('Subtitles requested')
		try:
			if mediaKey != '':
				key = mediaKey
			else:
				key = req.get_argument('key', 'missing')
			Log.Debug('Media rating key is %s' %(key))
			if key == 'missing':
				req.clear()
				req.set_status(412)
				req.finish('Missing rating key of media')
				return req
			getFile = req.get_argument('getFile', 'missing')
			Log.Debug('getFile is %s' %(getFile))
			# Path to media
			myURL='http://127.0.0.1:32400/library/metadata/' + key
			mediaInfo = []
			try:
				bDoGetTree = True
				# Only grap subtitle here
				streams = XML.ElementFromURL(myURL).xpath('//Stream[@streamType="3"]')					
				for stream in streams:
					subInfo = {}
					subInfo['key'] = stream.get('id')
					subInfo['codec'] = stream.get('codec')
					subInfo['selected'] = stream.get('selected')
					subInfo['languageCode'] = stream.get('languageCode')
					if stream.get('key') == None:
						location = 'Embedded'
					elif stream.get('format') == '':
						location = 'Agent'
					else:
						location = 'Sidecar'									
					subInfo['location'] = location
					# Get tree info, if not already done so, and if it's a none embedded srt, and we asked for all
					if getFile == 'true':
						if location != None:
							if bDoGetTree:							
								MediaStreams = XML.ElementFromURL(myURL + '/tree').xpath('//MediaStream')
								bDoGetTree = False
					if getFile == 'true':
						try:								
							for mediaStream in MediaStreams:				
								if mediaStream.get('id') == subInfo['key']:									
									subInfo['url'] = mediaStream.get('url')
						except:
							Log.Debug('Fatal error happened in getSubtitles')
							req.clear()
							req.set_status(500)
							req.set_header('Content-Type', 'application/json; charset=utf-8')
							req.finish('Fatal error happened in getSubtitles')
					mediaInfo.append(subInfo)	
			except:
				Log.Debug('Fatal error happened in getSubtitles')
				req.clear()
				req.set_status(500)
				req.set_header('Content-Type', 'application/json; charset=utf-8')
				req.finish('Fatal error happened in getSubtitles')
			if mediaKey != '':
				return mediaInfo
			else:
				req.clear()
				req.set_status(200)
				req.set_header('Content-Type', 'application/json; charset=utf-8')
				req.finish(json.dumps(mediaInfo))
		except:
			Log.Debug('Fatal error happened in getSubtitles')
			req.clear()
			req.set_status(500)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish('Fatal error happened in getSubtitles')

	''' get section '''
	def getSection(self,req):
		Log.Debug('Section requested')
		try:
			key = req.get_argument('key', 'missing')
			Log.Debug('Section key is %s' %(key))
			if key == 'missing':
				req.clear()
				req.set_status(412)
				req.finish('Missing key of section')
				return req
			start = req.get_argument('start', 'missing')
			Log.Debug('Section start is %s' %(start))
			if start == 'missing':
				req.clear()
				req.set_status(412)
				req.finish('Missing start of section')
				return req
			size = req.get_argument('size', 'missing')
			Log.Debug('Section size is %s' %(size))
			if size == 'missing':
				req.clear()
				req.set_status(412)
				req.finish('Missing size of section')
				return req
			getSubs = req.get_argument('getSubs', 'missing')
			# Got all the needed params, so lets grap the contents
			try:
				myURL = 'http://127.0.0.1:32400/library/sections/' + key + '/all?X-Plex-Container-Start=' + start + '&X-Plex-Container-Size=' + size
				rawSection = XML.ElementFromURL(myURL)
				Section=[]
				for media in rawSection:
					if getSubs != 'true':
						media = {'key':media.get('ratingKey'), 'title':media.get('title')}
					else:
						subtitles = self.getSubtitles(req, mediaKey=media.get('ratingKey'))
						media = {'key':media.get('ratingKey'), 'title':media.get('title'), 'subtitles':subtitles}
					Section.append(media)					
				Log.Debug('Returning %s' %(Section))
				req.clear()
				req.set_status(200)
				req.set_header('Content-Type', 'application/json; charset=utf-8')
				req.finish(json.dumps(Section))
			except:
				Log.Debug('Fatal error happened in getSection')
				req.clear()
				req.set_status(500)
				req.set_header('Content-Type', 'application/json; charset=utf-8')
				req.finish('Fatal error happened in getSection')
		except:
			Log.Debug('Fatal error happened in getSection')
			req.clear()
			req.set_status(500)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish('Fatal error happened in getSection')

	''' get sections list '''
	def getSectionsList(self,req):
		Log.Debug('Sections requested')
		try:
			rawSections = XML.ElementFromURL('http://127.0.0.1:32400/library/sections')
			Sections=[]
			for directory in rawSections:
				Section = {'key':directory.get('key'),'title':directory.get('title'),'type':directory.get('type')}
				Sections.append(Section)
			Log.Debug('Returning Sectionlist as %s' %(Sections))
			req.clear()
			req.set_status(200)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish(json.dumps(Sections))
		except:
			Log.Debug('Fatal error happened in getSectionsList')
			req.clear()
			req.set_status(500)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish('Fatal error happened in getSectionsList')

	''' Get a section size '''
	def getSectionSize(self, req):
		Log.Debug('Retrieve Section size')
		try:
			key = req.get_argument('key', 'missing')
			Log.Debug('Section key is %s' %(key))
			if key == 'missing':
				req.clear()
				req.set_status(412)
				req.finish("<html><body>Missing key of section</body></html>")
				return req
			else:
				myURL = 'http://127.0.0.1:32400/library/sections/' + key + '/all?X-Plex-Container-Start=0&X-Plex-Container-Size=0'
				try:
					section = XML.ElementFromURL(myURL)
					Log.Debug('Returning size as %s' %(section.get('totalSize')))
					req.clear()
					req.set_status(200)
					req.finish(section.get('totalSize'))
				except:					
					Log.Debug('Fatal error happened in GetSectionSize')
					req.clear()
					req.set_status(500)
					req.set_header('Content-Type', 'application/json; charset=utf-8')
					req.finish('Fatal error happened in GetSectionSize')
		except:
			Log.Debug('Fatal error happened in getSectionSize')
			req.clear()
			req.set_status(500)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish('Fatal error happened in getSectionSize')


