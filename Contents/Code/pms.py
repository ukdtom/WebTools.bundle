######################################################################################################################
#	pms helper unit				
# A WebTools bundle plugin	
#
#	Author: dane22, a Plex Community member
#
######################################################################################################################
from consts import NAME
import shutil, os
import time, json
import io, sys
from xml.etree import ElementTree

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
		Log.Exception('Fatal error happened in updateUASTypesCounters: ' + str(e))

#TODO fix updateAllBundleInfo
# updateAllBundleInfo
def updateAllBundleInfoFromUAS():
	def updateInstallDict():		
		# Start by creating a fast lookup cache for all uas bundles
		uasBundles = {}
		bundles = Dict['PMS-AllBundleInfo']
		for bundle in bundles:
			uasBundles[bundles[bundle]['identifier']] = bundle
		# Now walk the installed ones
		try:
			installed = Dict['installed'].copy()
			for installedBundle in installed:
				if not installedBundle.startswith('https://'):
					Log.Info('Checking unknown bundle: ' + installedBundle + ' to see if it is part of UAS now')
					if installedBundle in uasBundles:
						# Get the installed date of the bundle formerly known as unknown :-)
						installedBranch = Dict['installed'][installedBundle]['branch']
						installedDate = Dict['installed'][installedBundle]['date']
						# Add updated stuff to the dicts
						Dict['PMS-AllBundleInfo'][uasBundles[installedBundle]]['branch'] = installedBranch
						Dict['PMS-AllBundleInfo'][uasBundles[installedBundle]]['date'] = installedDate
						Dict['installed'][uasBundles[installedBundle]] = Dict['PMS-AllBundleInfo'][uasBundles[installedBundle]]
						# Remove old stuff from the Dict
						Dict['PMS-AllBundleInfo'].pop(installedBundle, None)
						Dict['installed'].pop(installedBundle, None)
						Dict.Save()
		except Exception, e:
			Log.Exception('Critical error in updateInstallDict while walking the gits: ' + str(e))
		return

	try:
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
			try:
				for git in gits:
					# Rearrange data
					key = git['repo']				
					installBranch = ''
					# Check if already present, and if an install date also is there
					installDate = ""
					CommitId = ""
					if key in Dict['PMS-AllBundleInfo']:
						jsonPMSAllBundleInfo = Dict['PMS-AllBundleInfo'][key]
						if 'date' in jsonPMSAllBundleInfo:
							installDate = Dict['PMS-AllBundleInfo'][key]['date']
						if 'CommitId' in jsonPMSAllBundleInfo:						
							CommitId = Dict['PMS-AllBundleInfo'][key]['CommitId']
					del git['repo']
					# Add/Update our Dict
					Dict['PMS-AllBundleInfo'][key] = git
					Dict['PMS-AllBundleInfo'][key]['date'] = installDate
					Dict['PMS-AllBundleInfo'][key]['CommitId'] = CommitId

			except Exception, e:
				Log.Exception('Critical error in updateAllBundleInfoFromUAS1 while walking the gits: ' + str(e))
			Dict.Save()
			updateUASTypesCounters()
			updateInstallDict()
		else:
			Log.Debug('UAS was sadly not present')
	except Exception, e:
		Log.Exception('Fatal error happened in updateAllBundleInfoFromUAS: ' + str(e))

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
		elif function == 'downloadSubtitle':
			return self.downloadSubtitle(req)
		elif function == 'tvShow':
			return self.TVshow(req)
		elif function == 'getAllBundleInfo':
			return self.getAllBundleInfo(req)
		elif function == 'getParts':
			return self.getParts(req)
		elif function == 'getSectionLetterList':
			return self.getSectionLetterList(req)
		elif function == 'getSectionByLetter':
			return self.getSectionByLetter(req)
		elif function == 'search':
			return self.search(req)
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

	''' Search for a title '''
	def search(self, req):
		Log.Info('Search called')
		try:
			title = req.get_argument('title', '_WT_missing_')
			if title == '_WT_missing_':
				req.clear()
				req.set_status(412)
				req.finish("<html><body>Missing title parameter</body></html>")
			else:
				url = 'http://127.0.0.1:32400/search?query=' + String.Quote(title)
				result = {}
				# Fetch search result from PMS
				foundMedias = XML.ElementFromURL(url)
				# Grap all movies from the result
				for media in foundMedias.xpath('//Video'):
					value = {}
					value['title'] = media.get('title')
					value['type'] = media.get('type')
					value['section'] = media.get('librarySectionID')			
					key = media.get('ratingKey')					
					result[key] = value
				# Grap results for TV-Shows
				for media in foundMedias.xpath('//Directory'):
					value = {}
					value['title'] = media.get('title')
					value['type'] = media.get('type')
					value['section'] = media.get('librarySectionID')			
					key = media.get('ratingKey')					
					result[key] = value
				Log.Info('Search returned: %s' %(result))
				req.clear()
				req.set_status(200)
				req.set_header('Content-Type', 'application/json; charset=utf-8')
				req.finish(json.dumps(result))
		except Exception, e:
			Log.Exception('Fatal error happened in search: ' + str(e))
			req.clear()
			req.set_status(500)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish('Fatal error happened in search: ' + str(e))

	''' Delete from an XML file '''
	def DelFromXML(self, fileName, attribute, value):
		Log.Debug('Need to delete element with an attribute named "%s" with a value of "%s" from file named "%s"' %(attribute, value, fileName))
		with io.open(fileName, 'r') as f:
			tree = ElementTree.parse(f)
			root = tree.getroot()
			mySubtitles = root.findall('.//Subtitle')
			for Subtitles in root.findall("Language[Subtitle]"):
				for node in Subtitles.findall("Subtitle"):
					myValue = node.attrib.get(attribute)
					if myValue:
						if '_' in myValue:
							drop, myValue = myValue.split("_")
						if myValue == value:
							Subtitles.remove(node)
		tree.write(fileName, encoding='utf-8', xml_declaration=True)
		return

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
			Log.Exception('Fatal error happened in getParts: ' + str(e))
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
			Log.Exception('Fatal error happened in uploadFile: ' + str(e))
			req.clear()
			req.set_status(500)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish('Fatal error happened in uploadFile: ' + str(e))

	# getAllBundleInfo
	def getAllBundleInfo(self, req):
		Log.Debug('Got a call for getAllBundleInfo')
		api = req.get_argument('api', '2')
		try:
			req.clear()
			Log.Debug('Returning: ' + str(len(Dict['PMS-AllBundleInfo'])) + ' items')		
			req.set_status(200)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			if api == '3':
				retArray = []
				for key, value in Dict['PMS-AllBundleInfo'].items():
					d = {}
					d[key] = value
					retArray.append(d)
				Log.Debug('Returning V3: ' + str(len(Dict['PMS-AllBundleInfo'])) + ' items')
				req.finish(json.dumps(retArray))
			else:
				Log.Debug('Returning V2: ' + str(len(Dict['PMS-AllBundleInfo'])) + ' items')
				req.finish(json.dumps(Dict['PMS-AllBundleInfo']))
		except Exception, e:
			Log.Exception('Fatal error happened in getAllBundleInfo: ' + str(e))
			req.clear()

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
				except Exception, e:
					Log.Exception("Unable to remove the bundle directory: " + str(e))
					req.clear()
					req.set_status(500)
					req.set_header('Content-Type', 'application/json; charset=utf-8')
					req.finish('Fatal error happened when trying to remove the bundle directory: ' + str(e))
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
					if 'Unknown' in Dict['PMS-AllBundleInfo'][url]['type']:
						# Manual install or migrated, so nuke the entire key
						Dict['PMS-AllBundleInfo'].pop(url, None)
					else:
						# UAS bundle, so only nuke date field
						git = Dict['PMS-AllBundleInfo'][url]
						git['date'] = ''
						Dict['PMS-AllBundleInfo'][url] = git
				else:
					# Manual install or migrated, so nuke the entire key
					Dict['PMS-AllBundleInfo'].pop(url, None)
				Dict.Save()
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
				Log.Exception('Fatal error happened in removeBundle: ' + str(e))
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
		except Exception, e:
			Log.Exception('Fatal error happened in delBundle: %s' %(e))
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
						# Path to symblink
						filePath = filePath.replace('media:/', os.path.join(Core.app_support_path, 'Media', 'localhost'))
						try:
							# Subtitle name
							agent, sub = filePath.rsplit('_',1)
							tmp, agent = agent.split('com.')
							# Agent used
							agent = 'com.' + agent
							filePath2 = filePath.replace('Contents', os.path.join('Contents', 'Subtitle Contributions'))
							filePath2, language = filePath2.split('Subtitles')
							language = language[1:3]	
							filePath3 = os.path.join(filePath2[:-1], agent, language, sub)
						except Exception, e:
							Log.Exception('Exception in delSub generation file Path: ' + str(e))
						subtitlesXMLPath, tmp = filePath.split('Contents')
						agentXMLPath = os.path.join(subtitlesXMLPath, 'Contents', 'Subtitle Contributions', agent + '.xml')							
						subtitlesXMLPath = os.path.join(subtitlesXMLPath, 'Contents', 'Subtitles.xml')
						self.DelFromXML(agentXMLPath, 'media', sub)
						self.DelFromXML(subtitlesXMLPath, 'media', sub)
						# Nuke the actual file
						try:
							# Delete the actual file
							os.remove(filePath)
							# Delete the symb link
							os.remove(filePath3)
							#TODO: Refresh is sadly not working for me, so could use some help here :-(
							#Let's refresh the media
							url = 'http://127.0.0.1:32400/library/metadata/' + key + '/refresh?force=1'
							HTTP.Request(url, cacheTime=0, immediate=True, method="PUT")
						except Exception, e:
							Log.Exception('Exception while deleting an agent based sub: ' + str(e))
							req.clear()
							req.set_status(404)
							req.set_header('Content-Type', 'application/json; charset=utf-8')
							req.finish('Exception while deleting an agent based sub: ' + str(e))
						retValues = {}
						retValues['FilePath']=filePath3
						retValues['SymbLink']=filePath
						Log.Debug('Agent subtitle returning %s' %(retValues))
						req.clear()
						req.set_status(200)
						req.set_header('Content-Type', 'application/json; charset=utf-8')
						req.finish(json.dumps(retValues))
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
						except Exception, e:
							# Could not find req. subtitle
							Log.Exception('Fatal error happened in delSub, when deleting ' + filePath + ' : ' + str(e))
							req.clear()
							req.set_status(404)
							req.set_header('Content-Type', 'application/json; charset=utf-8')
							req.finish('Fatal error happened in delSub, when deleting %s : %s' %(filePath, str(e)))
			else:
				# Could not find req. subtitle
				Log.Debug('Fatal error happened in delSub, subtitle not found')
				req.clear()
				req.set_status(404)
				req.set_header('Content-Type', 'application/json; charset=utf-8')
				req.finish('Could not find req. subtitle')
		except Exception, e:
			Log.Exception('Fatal error happened in delSub: ' + str(e))
			req.clear()
			req.set_status(500)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish('Fatal error happened in delSub: ' + str(e))

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
			except Exception, e:
				Log.Exception('Fatal error happened in TV-Show while fetching season: %s' %(e))
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
			except Exception, e:
				Log.Exception('Fatal error happened in TV-Show while fetching seasons: %s' %(e))
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
				Log.Exception('Fatal error happened in TV-Show while fetching size %s' %(e))
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
			except Exception, e:
				Log.Exception('Fatal error happened in TV-Show while fetching contents %s' %(e))
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
		except Exception, e:
			Log.Exception('Fatal error happened in TVshow: %s' %(e))
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
			except Exception, e:
				Log.Exception('Fatal error happened in showSubtitle: %s' %(e))
				req.clear()
				req.set_status(500)
				req.set_header('Content-Type', 'application/json; charset=utf-8')
				req.finish('Fatal error happened in showSubtitle')
		except Exception, e:
			Log.Exception('Fatal error happened in showSubtitle: %s' %(e))
			req.clear()
			req.set_status(500)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish('Fatal error happened in showSubtitle')

	''' Download Subtitle '''
	def downloadSubtitle(self, req):
		Log.Debug('Download Subtitle requested')
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
				# Grab the subtitle
				try:
					response = HTML.StringFromElement(HTML.ElementFromURL(myURL))
				except Exception, e:
					Log.Exception('Fatal error happened in downloadSubtitle: ' + str(e))
					req.clear()
					req.set_status(401)
					req.set_header('Content-Type', 'application/json; charset=utf-8')
					req.finish('Fatal error happened in downloadSubtitle: ' + str(e))			
				# Make it nicer
				response = response.replace('<p>', '',1)
				response = response.replace('</p>', '',1)
				response = response.replace('&gt;', '>')
				response = response.split('\n')
				# Prep the download http headers
				req.set_header ('Content-Disposition', 'attachment; filename="subtitle.srt"')
				req.set_header('Cache-Control', 'no-cache')
				req.set_header('Pragma', 'no-cache')
				req.set_header('Content-Type', 'application/text/plain')				
				# Download the sub
				try:
					for line in response:
						req.write(line + '\n')
					req.finish()
					return req
				except Exception, e:
					Log.Exception('Fatal error happened in downloadSubtitle: ' + str(e))
					req.clear()
					req.set_status(500)
					req.set_header('Content-Type', 'application/json; charset=utf-8')
					req.finish('Fatal error happened in downloadSubtitle: ' + str(e))
			except Exception, e:
				Log.Exception('Fatal error happened in downloadSubtitle: %s' %(e))
				req.clear()
				req.set_status(500)
				req.set_header('Content-Type', 'application/json; charset=utf-8')
				req.finish('Fatal error happened in showSubtitle')
		except Exception, e:
			Log.Exception('Fatal error happened in downloadSubtitle: %s' %(e))
			req.clear()
			req.set_status(500)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish('Fatal error happened in downloadSubtitle')

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
					elif stream.get('format') == None:
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
						except Exception, e:
							Log.Exception('Fatal error happened in getSubtitles: %s' %(e))
							req.clear()
							req.set_status(500)
							req.set_header('Content-Type', 'application/json; charset=utf-8')
							req.finish('Fatal error happened in getSubtitles')
					mediaInfo.append(subInfo)	
			except Exception, e:
				Log.Exception('Fatal error happened in getSubtitles %s' %(e))
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
		except Exception, e:
			Log.Exception('Fatal error happened in getSubtitles: %s' %(e))
			req.clear()
			req.set_status(500)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish('Fatal error happened in getSubtitles')

	''' get section letter-list '''
	def getSectionLetterList(self, req):
		Log.Debug('Section requested')
		try:
			key = req.get_argument('key', 'missing')
			Log.Debug('Section key is %s' %(key))
			if key == 'missing':
				req.clear()
				req.set_status(412)
				req.finish('Missing key of section')
				return req
			# Got all the needed params, so lets grap the list
			myURL = 'http://127.0.0.1:32400/library/sections/' + key + '/firstCharacter'
			resultJson = { }			
			sectionLetterList = XML.ElementFromURL(myURL).xpath('//Directory')
			for sectionLetter in sectionLetterList:
				resultJson[sectionLetter.get('title')] = {
													'key' : sectionLetter.get('key'), 'size': sectionLetter.get('size')}					
			Log.Debug('Returning %s' %(resultJson))
			req.clear()
			req.set_status(200)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish(json.dumps(resultJson, sort_keys=True))
		except Exception, e:
			Log.Exception('Fatal error happened in getSectionLetterList: %s ' %(str(e)))
			req.clear()
			req.set_status(500)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish('Fatal error happened in getSectionLetterList: ' + str(e))

	''' get getSectionByLetter '''
	def getSectionByLetter(self,req):
		Log.Debug('getSectionByLetter requested')
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
			letterKey = req.get_argument('letterKey', 'missing')
			Log.Debug('letterKey is %s' %(letterKey))
			if letterKey == 'missing':
				req.clear()
				req.set_status(412)
				req.finish('Missing letterKey')
				return req
			getSubs = req.get_argument('getSubs', 'missing')
			# Got all the needed params, so lets grap the contents
			try:
				myURL = 'http://127.0.0.1:32400/library/sections/' + key + '/firstCharacter/' + letterKey + '?X-Plex-Container-Start=' + start + '&X-Plex-Container-Size=' + size
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
			except Exception, e:
				Log.Exception('Fatal error happened in getSectionByLetter: ' + str(e))
				req.clear()
				req.set_status(500)
				req.set_header('Content-Type', 'application/json; charset=utf-8')
				req.finish('Fatal error happened in getSectionByLetter: ' + str(e))
		except Exception, e:
			Log.Exception('Fatal error happened in getSectionByLetter: ' + str(e))
			req.clear()
			req.set_status(500)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish('Fatal error happened in getSectionByLetter: ' + str(e))

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
			except Exception, e:
				Log.Exception('Fatal error happened in getSection %s' %(str(e)))
				req.clear()
				req.set_status(500)
				req.set_header('Content-Type', 'application/json; charset=utf-8')
				req.finish('Fatal error happened in getSection')
		except Exception, e:
			Log.Exception('Fatal error happened in getSection: %s' %(str(e)))
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
		except Exception, e:
			Log.Exception('Fatal error happened in getSectionsList: %s' %(str(e)))
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
				except Exception, e:	
					Log.Exception('Fatal error happened in GetSectionSize: %s' %(str(e)))
					req.clear()
					req.set_status(500)
					req.set_header('Content-Type', 'application/json; charset=utf-8')
					req.finish('Fatal error happened in GetSectionSize')
		except Exception, e:
			Log.Exception('Fatal error happened in getSectionSize: %s' %(str(e)))
			req.clear()
			req.set_status(500)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish('Fatal error happened in getSectionSize')


