######################################################################################################################
#	Git bundles helper unit
# A WebTools bundle plugin					
#
#	Author: dane22, a Plex Community member
#
# Handles all comm. with Github
######################################################################################################################

import datetime			# Used for a timestamp in the dict
import json
import io, os
import plistlib
import pms

class git(object):
	# Defaults used by the rest of the class
	def __init__(self):
		Log.Debug('******* Starting git *******')
		self.url = ''
		self.PLUGIN_DIR = Core.storage.join_path(Core.app_support_path, Core.config.bundles_dir_name)
		self.UAS_URL = 'https://github.com/ukdtom/UAS2Res'
		self.IGNORE_BUNDLE = ['WebTools.bundle', 'SiteConfigurations.bundle']
		Log.Debug("Plugin directory is: %s" %(self.PLUGIN_DIR))

	''' Grap the tornado req, and process it '''
	def reqprocess(self, req):	
		function = req.get_argument('function', 'missing')
		if function == 'missing':
			req.clear()
			req.set_status(412)
			req.finish("<html><body>Missing function parameter</body></html>")
		elif function == 'getGit':
			# Call install with the url
			return self.install(req)	
		elif function == 'list':
			return self.list(req)
		elif function == 'getLastUpdateTime':
			return self.getLastUpdateTime(req)
		elif function == 'getListofBundles':
			return self.getListofBundles(req)
		elif function == 'getReleaseInfo':
			return self.getReleaseInfo(req)
		elif function == 'updateUASCache':
			return self.updateUASCache(req)
		elif function == 'uasTypes':
			return self.uasTypes(req)
		elif function == 'getUpdateList':
			return self.getUpdateList(req)
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
		elif function == 'migrate':
			return self.migrate(req)
		else:
			req.clear()
			req.set_status(412)
			req.finish("<html><body>Unknown function call</body></html>")

	''' This function will return a list of bundles, where there is an update avail '''
	def getUpdateList(self, req):
		Log.Debug('Got a call for getUpdateList')
		try:
			# Are there any bundles installed?
			if 'installed' in Dict:
				bundles = Dict['installed']
				Log.Debug('Installed channes are: ' + str(bundles))
				result = {}
				# Now walk them one by one
				for bundle in bundles:
					if bundle.startswith('https://github'):
						gitTime = self.getLastUpdateTime(req, UAS=True, url=bundle)
						sBundleTime = Dict['installed'][bundle]['date']
						bundleTime = datetime.datetime.strptime(sBundleTime, '%Y-%m-%d %H:%M:%S')
						if bundleTime < gitTime:
							gitInfo = Dict['installed'][bundle]
							gitInfo['gitHubTime'] = str(gitTime)
							result[bundle] = gitInfo
				Log.Debug('Updates avail: ' + str(result))
				req.clear()
				req.set_status(200)
				req.set_header('Content-Type', 'application/json; charset=utf-8')
				req.finish(result)
			else:
				Log.Debug('No bundles are installed')
				req.clear()
				req.set_status(204)
		except Exception, e:
			Log.Debug('Fatal error happened in getUpdateList: ' + str(e))
			req.clear()
			req.set_status(500)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish('Fatal error happened in getUpdateList' + str(e))
	

	''' This function will migrate bundles that has been installed without using our UAS into our UAS '''
	def migrate(self, reg):
		# get list from uas cache
		def getUASCacheList():
			try:
				jsonFileName = Core.storage.join_path(self.PLUGIN_DIR, NAME + '.bundle', 'http', 'uas', 'Resources', 'plugin_details.json')
				json_file = io.open(jsonFileName, "rb")
				response = json_file.read()
				json_file.close()	
				gits = JSON.ObjectFromString(str(response))
				# Walk it, and reformat to desired output
				results = {}
				for git in gits:
					result = {}
					title = git['repo']
					del git['repo']
					results[title] = git
				return results	
			except Exception, e:
				Log.Debug('Exception in Migrate/getUASCacheList : ' + str(e))				
				return ''

		# Grap indentifier from plist file
		def getIdentifier(pluginDir):
			try:
				pFile = Core.storage.join_path(self.PLUGIN_DIR, pluginDir, 'Contents', 'Info.plist')
				pl = plistlib.readPlist(pFile)
				createStamp = datetime.datetime.fromtimestamp(os.path.getmtime(pFile)).strftime('%Y-%m-%d %H:%M:%S')			
				return (pl['CFBundleIdentifier'], createStamp)
			except Exception, e:
				Log.Debug('Exception in Migrate/getIdentifier : ' + str(e))				
				return ''

		# Main call
		Log.Debug('Migrate function called')
		try:
			# Init dict, if not already so
			if Dict['installed'] == None:
				Dict['installed'] = {}
			# Let's start by getting a list of known installed bundles
			knownBundles = []
			for installedBundles in Dict['installed']:
				knownBundles.append(Dict['installed'][installedBundles]['bundle'])
			# Grap a list of directories in the plugin dir
			dirs = os.listdir(self.PLUGIN_DIR)
			for pluginDir in dirs:
				if pluginDir.endswith('.bundle'):
					# It's a bundle
					if pluginDir not in knownBundles:
						# It's unknown
						if pluginDir not in self.IGNORE_BUNDLE:
							Log.Debug('About to migrate %s' %(pluginDir))
							# This we need to migrate
							(target, dtStamp) = getIdentifier(pluginDir)
							# try and see if part of uas Cache
							uasListjson = getUASCacheList()
							bFound = False
							for git in uasListjson:
								if target == uasListjson[git]['identifier']:
									Log.Debug('Found %s is part of uas' %(target))
									targetGit = {}
									targetGit['description'] = uasListjson[git]['description']
									targetGit['title'] = uasListjson[git]['title']
									targetGit['bundle'] = uasListjson[git]['bundle']
									targetGit['branch'] = uasListjson[git]['branch']
									targetGit['identifier'] = uasListjson[git]['identifier']
									targetGit['type'] = uasListjson[git]['type']
									targetGit['icon'] = uasListjson[git]['icon']
									targetGit['date'] = dtStamp
									Dict['installed'][git] = targetGit
									Log.Debug('Dict stamped with the following install entry: ' + git + ' - '  + str(targetGit))
									# Now update the PMS-AllBundleInfo Dict as well
									Dict['PMS-AllBundleInfo'][git] = targetGit
									Dict.Save()
									bFound = True
									break
							if not bFound:
								Log.Debug('Found %s is sadly not part of uas' %(pluginDir))
								git = {}
								git['title'] = pluginDir[:-7]
								git['description'] = ''
								git['branch'] = ''
								git['bundle'] = pluginDir
								git['identifier'] = target
								git['type'] = ['Unknown']
								git['icon'] = ''
								git['date'] = dtStamp
								Dict['installed'][target] = git
								# Now update the PMS-AllBundleInfo Dict as well
								Dict['PMS-AllBundleInfo'][target] = git

								Log.Debug('Dict stamped with the following install entry: ' + pluginDir + ' - '  + str(git))
								Dict.Save()
		except Exception, e:
			Log.Debug('Fatal error happened in migrate: ' + str(e))
			req.clear()
			req.set_status(500)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish('Fatal error happened in migrate: ' + str(e))
			return req

	''' This will return a list of UAS bundle types from the UAS Cache '''
	def uasTypes(self, req):
		Log.Debug('Starting uasTypes')
		try:
			req.clear()
			req.set_status(200)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish(json.dumps(Dict['uasTypes']))
		except Exception, e:
			Log.Debug('Exception in uasTypes: ' + str(e))
			req.clear()
			req.set_status(500)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish('Fatal error happened in uasTypes: ' + str(e))
			return req

	''' This will update the UAS Cache directory from GitHub '''
	def updateUASCache(self, req):
		Log.Debug('Starting to update the UAS Cache')

		def updateUASTypes(req):
			Log.Debug('Starting to update the UAS Bundle types')
			try:
				# Grap contents of json file
				jsonFileName = Core.storage.join_path(self.PLUGIN_DIR, NAME + '.bundle', 'http', 'uas', 'Resources', 'plugin_details.json')
				json_file = io.open(jsonFileName, "rb")
				bundleFile = json_file.read()
				json_file.close()
				bundles = json.loads(bundleFile)
				uasTypes  = []
				for entry in bundles:
					typeList = entry['type']
					for bundleType in typeList:
						if bundleType not in uasTypes:
							uasTypes.append(bundleType)	
				uasTypes.append('Unknown')				
				Dict['uasTypes'] = uasTypes
				Dict.Save()
				return
			except:
				Log.Debug('Exception in UASType update...Ignorring')

		# Start by getting the time stamp for the last update
		try:
			lastUpdateUAS = Dict['UAS']
			updateUASTypes(req)
			Log.Debug('Last update time for UAS Cache is: %s' %(lastUpdateUAS))
			if lastUpdateUAS == None:
				# Not set yet, so default to Linux start date
				lastUpdateUAS = datetime.datetime.strptime('01-01-1970 00:00:00', '%m-%d-%Y %H:%M:%S')
			# Now get the last update time from the UAS repository on GitHub
			masterUpdate = self.getLastUpdateTime(req, True, self.UAS_URL)
			# Do we need to update the cache, and add 2 min. tolerance here?
			if (masterUpdate - lastUpdateUAS) > datetime.timedelta(seconds = 120):
				# We need to update UAS Cache
				# Target Directory
				targetDir = Core.storage.join_path(self.PLUGIN_DIR, NAME + '.bundle', 'http', 'uas')
				# Force creation, if missing
				Core.storage.ensure_dirs(targetDir)
				# Grap file from Github
				zipfile = Archive.ZipFromURL(self.UAS_URL+ '/archive/master.zip')
				for filename in zipfile:
					# Walk contents of the zip, and extract as needed
					data = zipfile[filename]
					if not str(filename).endswith('/'):
						# Pure file, so save it				
						path = self.getSavePath(targetDir, filename)
						Log.Debug('Extracting file' + path)
						try:
							Core.storage.save(path, data)
						except Exception, e:
							bError = True
							Log.Debug("Unexpected Error")
					else:
						# We got a directory here
						Log.Debug(filename.split('/')[-2])
						if not str(filename.split('/')[-2]).startswith('.'):
							# Not hidden, so let's create it
							path = self.getSavePath(targetDir, filename)
							Log.Debug('Extracting folder ' + path)
							try:
								Core.storage.ensure_dirs(path)
							except Exception, e:
								bError = True
								Log.Debug("Unexpected Error")
				# UAS Cache has been updated, so time to update the UAS bundle types
				try:
					updateUASTypes(req)
				except:
					req.clear()
					req.set_status(500)
					req.set_header('Content-Type', 'application/json; charset=utf-8')
					req.finish('Fatal error happened in updateUASTypes')
					return req				
				# Update the AllBundleInfo as well
				pms.updateAllBundleInfoFromUAS()
			else:
				Log.Debug('UAS Cache already up to date')
			# Set timestamp in the Dict
			Dict['UAS'] = datetime.datetime.now()
			req.clear()
			req.set_status(200)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish('UASCache is up to date')	
		except Exception, e:
			Log.Debug('Exception in updateUASCache ' + str(e)) 
			req.clear()
			req.set_status(500)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish('Exception in updateUASCache ' + str(e))
			return req

	''' list will return a list of all installed gits from GitHub'''
	def list(self, req):
		if 'installed' in Dict:
			Log.Debug('Installed channes are: ' + str(Dict['installed']))
			req.clear()
			req.set_status(200)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish(json.dumps(Dict['installed']))
		else:
			Log.Debug('installed dict not found')
			req.clear()
			req.set_status(204)

	def getSavePath(self, plugin, path):
		fragments = path.split('/')[1:]
		# Remove the first fragment if it matches the bundle name
		if len(fragments) and fragments[0].lower() == plugin.lower():
			fragments = fragments[1:]
		return Core.storage.join_path(plugin, *fragments)

	''' Download install/update from GitHub '''
	def install(self, req):

		''' Grap bundle name '''
		def grapBundleName(url):	
			gitName = url.rsplit('/', 1)[-1]
			# Forgot to name git to end with .bundle?
			if not gitName.endswith('.bundle'):
				gitName = gitName + '.bundle'
			gitName = Core.storage.join_path(self.PLUGIN_DIR, gitName)
			Log.Debug('Bundle directory name digested as: %s' %(gitName))
			return gitName

		''' Save Install info to the dict '''
		def saveInstallInfo(url, bundleName):
			# Get the dict with the installed bundles, and init it if it doesn't exists
			if not 'installed' in Dict:
				Dict['installed'] = {}

			# Start by loading the UAS Cache file list
			jsonFileName = Core.storage.join_path(self.PLUGIN_DIR, NAME + '.bundle', 'http', 'uas', 'Resources', 'plugin_details.json')
			json_file = io.open(jsonFileName, "rb")
			response = json_file.read()
			json_file.close()
			# Convert to a JSON Object
			gits = JSON.ObjectFromString(str(response))
			bNotInUAS = True
			# Walk the one by one, so we can handle upper/lower case
			for git in gits:
				if url.upper() == git['repo'].upper():
					key = git['repo']
					del git['repo']
					git['date'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
					Dict['installed'][key] = git
					bNotInUAS = False
					Log.Debug('Dict stamped with the following install entry: ' + key + ' - '  + str(git))
					# Now update the PMS-AllBundleInfo Dict as well
					Dict['PMS-AllBundleInfo'][key] = git
					break
			if bNotInUAS:
				key = url
				pFile = Core.storage.join_path(self.PLUGIN_DIR, bundleName, 'Contents', 'Info.plist')
				pl = plistlib.readPlist(pFile)
				git = {}
				git['title'] = bundleName[bundleName.rfind("/"):][1:][:-7]
				git['description'] = ''
				git['branch'] = ''
				git['bundle'] = bundleName[bundleName.rfind("/"):][1:]
				git['identifier'] = pl['CFBundleIdentifier']
				git['type'] = ['Unknown']
				git['icon'] = ''
				git['date'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
				Dict['installed'][key] = git
				# Now update the PMS-AllBundleInfo Dict as well
				Dict['PMS-AllBundleInfo'][key] = git
				Log.Debug('Dict stamped with the following install entry: ' + key + ' - '  + str(git))
			Dict.Save()
			return

		''' Download the bundle '''
		def downloadBundle2tmp(url, bundleName):
			try:
				zipPath = url + '/archive/master.zip'
				# Grap file from Github
				zipfile = Archive.ZipFromURL(zipPath)
				# Create base directory
				Core.storage.ensure_dirs(Core.storage.join_path(self.PLUGIN_DIR, bundleName))
				# Make sure it's actually a bundle channel
				bError = True
				for filename in zipfile:
					if '/Contents/Info.plist' in filename:
						# We found the info.plist file here, but is the dir level okay?
						if Platform.OS == 'Windows':
							count = filename.count('\\')
						else:
							count = filename.count('/')		
						if count == 2:
							bError = False
						else:
							Log.Critical('Tried to install ' + bundleName + ' but dir levels did not match')				
				if bError:
					Core.storage.remove_tree(Core.storage.join_path(self.PLUGIN_DIR, bundleName))
					Log.Debug('The bundle downloaded is not a Plex Channel bundle!')
					raise ValueError('The bundle downloaded is not a Plex Channel bundle!')
				bError = False
				for filename in zipfile:
					# Walk contents of the zip, and extract as needed
					data = zipfile[filename]
					if not str(filename).endswith('/'):
						# Pure file, so save it				
						path = self.getSavePath(bundleName, filename)
						Log.Debug('Extracting file' + path)
						try:
							Core.storage.save(path, data)
						except Exception, e:
							bError = True
							Log.Debug("Unexpected Error")
					else:
						# We got a directory here
						Log.Debug(filename.split('/')[-2])
						if not str(filename.split('/')[-2]).startswith('.'):
							# Not hidden, so let's create it
							path = self.getSavePath(bundleName, filename)
							Log.Debug('Extracting folder ' + path)
							try:
								Core.storage.ensure_dirs(path)
							except Exception, e:
								bError = True
								Log.Debug("Unexpected Error")
				if not bError:
					# Install went okay, so save info
					saveInstallInfo(url, bundleName)
					return True
			except:
				return False

		# Starting install main
		Log.Debug('Starting install')
		req.clear()
		url = req.get_argument('url', 'missing')
		if url == 'missing':
			req.set_status(412)
			req.finish("<html><body>Missing url of git</body></html>")
			return req
		# Get bundle name
		bundleName = grapBundleName(url)
		if downloadBundle2tmp(url, bundleName):
			Log.Debug('Finished installing %s' %(bundleName))
			Log.Debug('******* Ending install *******')
			req.clear()
			req.set_status(200)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish('All is cool')
			return req
		else:
			req.set_status(500)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish('Fatal error happened in install for :' + url)
			return req

	''' Get the last update time for a master branch. if UAS is set to True, then this is an internal req. for UAS '''
	def getLastUpdateTime(self, req, UAS=False, url=''):
		Log.Debug('Starting getLastUpdateTime')
		Log.Debug('URL is: ' + url)
		# Wanted to internally check for UAS update?
		if not UAS:			
			url = req.get_argument('url', 'missing')
			Log.Debug('URL2 is: ' + url)
		if url == 'missing':
			req.clear()
			req.set_status(412)
			req.finish("<html><body>Missing url of git</body></html>")
			return req
		try:
			Log.Debug('URL3 is: ' + url)
			url += '/commits/master.atom'
			response = Datetime.ParseDate(HTML.ElementFromURL(url).xpath('//entry')[0].xpath('./updated')[0].text[:-6])
			Log.Debug('Last update for: ' + url + ' is: ' + str(response))
			if UAS:
				return response
			else:
				req.clear()
				req.set_status(200)
				req.set_header('Content-Type', 'application/json; charset=utf-8')
				req.finish(str(response))
		except:
			Log.Debug('Fatal error happened in getLastUpdateTime for :' + url)
			req.clear()
			req.set_status(500)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish('Fatal error happened in getLastUpdateTime for :' + url)

	''' Get list of avail bundles in the UAS '''
	def getListofBundles(self, req):
		Log.Debug('Starting getListofBundles')
		try:
			jsonFileName = Core.storage.join_path(self.PLUGIN_DIR, NAME + '.bundle', 'http', 'uas', 'Resources', 'plugin_details.json')
			json_file = io.open(jsonFileName, "rb")
			response = json_file.read()
			json_file.close()	
			gits = JSON.ObjectFromString(str(response))
			# Walk it, and reformat to desired output
			results = {}
			for git in gits:
				result = {}
				title = git['repo']
				del git['repo']
				results[title] = git	
			Log.Debug('getListofBundles returned: ' + str(results))
			req.clear()
			req.set_status(200)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish(json.dumps(results))
		except:
			Log.Debug('Fatal error happened in getListofBundles')
			req.clear()
			req.set_status(500)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish('Fatal error happened in getListofBundles')

	''' Get release info for a bundle '''
	def getReleaseInfo(self, req):
		Log.Debug('Starting getReleaseInfo')
		try:
			url = req.get_argument('url', 'missing')
			if url == 'missing':
				req.clear()
				req.set_status(412)
				req.finish("<html><body>Missing url of git</body></html>")
				return req
			version = req.get_argument('version', 'latest')
			# Switch to https, if not already so
			url = url.replace('http://', 'https://',1)
			# Switch to use the api
			url = url.replace('https://github.com/', 'https://api.github.com/repos/', 1)
			# Add the requested version of the release info
			if version == 'latest':
				url += '/releases/latest'
			elif version == 'all':
				url += '/releases'
			else:
				# Unknown version request. [latest, all] is supported
				req.clear()
				req.set_status(412)
				req.finish("<html><body>Unknown version</body></html>")
				return req
			# return the result
			Log.Debug('Getting release info from url: ' + url)
			response = HTML.StringFromElement(HTML.ElementFromURL(url))
			# Remove html code
			response = response.replace('<p>', '', 1)
			response = response.replace('</p>', '', 1)
			Log.Debug('***** Got the following from github *****')
			Log.Debug(response)
			req.clear()
			req.set_status(200)
			req.finish(response)
			Log.Debug('Ending getReleaseInfo')
		except:
			Log.Debug('Fatal error happened in getReleaseInfo')
			req.clear()
			req.set_status(500)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish('Fatal error happened in getInfo')

