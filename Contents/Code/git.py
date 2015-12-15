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
import io

class git(object):
	# Defaults used by the rest of the class
	def __init__(self):
		Log.Debug('******* Starting git *******')
		self.url = ''
		self.PLUGIN_DIR = Core.storage.join_path(Core.app_support_path, Core.config.bundles_dir_name)
		self.UAS_URL = 'https://github.com/ukdtom/UAS2Res'
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
		else:
			req.clear()
			req.set_status(412)
			req.finish("<html><body>Unknown function call</body></html>")

	''' This will return a list of UAS bundle types from the UAS Cache '''
	def uasTypes(self, req):
		Log.Debug('Starting uasTypes')
		try:
			req.clear()
			req.set_status(200)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish(json.dumps(Dict['uasTypes']))
		except:
			req.clear()
			req.set_status(500)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish('Fatal error happened in uasTypes')
			return req

	''' This will update the UAS Cache directory from GitHub '''
	def updateUASCache(self, req):
		Log.Debug('Starting to update the UAS Cache')

		def updateUASTypes(req):
			Log.Debug('Starting to update the UAS Bundle types')
			try:
				print 'Ged start updateUASTypes'
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
				Dict['uasTypes'] = uasTypes
				return req
			except:
				req.clear()
				req.set_status(500)
				req.set_header('Content-Type', 'application/json; charset=utf-8')
				req.finish('Fatal error happened in updateUASTypes')
				return req

		# Start by getting the time stamp for the last update
		try:
			lastUpdateUAS = Dict['UAS']


			print 'GED Forced typelist'
			updateUASTypes(req)


			Log.Debug('Last update time for UAS Cache is: %s' %(lastUpdateUAS))
			if lastUpdateUAS == None:
				# Not set yet, so default to Linux start date
				lastUpdateUAS = datetime.datetime.strptime('01-01-1970 00:00:00', '%m-%d-%Y %H:%M:%S')
			# Now get the last update time from the UAS repository on GitHub
			masterUpdate = self.getLastUpdateTime(req, True)
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
			else:
				Log.Debug('UAS Cache already up to date')
			# Set timestamp in the Dict
			Dict['UAS'] = datetime.datetime.now()

			# UAS Cache has been updated, so time to update the UAS bundle types
			try:
				updateUASTypes(req)
			except:
				req.clear()
				req.set_status(500)
				req.set_header('Content-Type', 'application/json; charset=utf-8')
				req.finish('Fatal error happened in updateUASTypes')
				return req
			req.clear()
			req.set_status(200)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish('UASCache is up to date')	
		except:
			req.clear()
			req.set_status(500)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish('Fatal error happened in updateUASCache')
			return req

	''' list will return a list of all installed gits from GitHub'''
	def list(self, req):
		if 'installed' in Dict:
			Log.Debug('Installed channes are: ' + str(Dict['installed']))
			req.clear()
			req.set_status(200)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish(Dict['installed'])
		else:
			Log.Debug('installed dict not found')
			req.clear()
			req.set_status(404)			
			req.finish("<html><body>Could not find any installed bundles from WebTools</body></html>")

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
			installedBundle = bundleName[bundleName.rfind("/"):][1:][:-7]
			# Get the dict with the installed bundles
			if not 'installed' in Dict:
				Dict['installed'] = {}
			# Does it already contains the bundle just installed?
			if not installedBundle in Dict['installed']:
				# Add initial key
				Dict['installed'][installedBundle] = {}
			Dict['installed'][installedBundle]['date'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
			Dict['installed'][installedBundle]['url'] = url
			Dict['installed'][installedBundle]['version'] = 'future'
			Log.Debug('Dict stamped with the following install entry: ' + installedBundle + ' - '  + str(Dict['installed'][installedBundle]))
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
					if '/Contents/Code/__init__.py' in filename:
						bError = False
				if bError:
					print 'NOT A CHANNEL'
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
		url = req.get_argument('url', 'missing')
		if url == 'missing':
			req.clear()
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
			req.clear()
			req.set_status(500)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish('Fatal error happened in install for :' + url)
			return req

	''' Get the last update time for a master branch. if UAS is set to True, then this is an internal req. for UAS '''
	def getLastUpdateTime(self, req, UAS=False):
		Log.Debug('Starting getLastUpdateTime')
		# Wanted to internally check for UAS update?
		if UAS:
			url = self.UAS_URL
		else:
			url = req.get_argument('url', 'missing')
		if url == 'missing':
			req.clear()
			req.set_status(412)
			req.finish("<html><body>Missing url of git</body></html>")
			return req
		try:
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
			Log.Debug('getListofBundles returned: ' + str(response))
			req.clear()
			req.set_status(200)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish(str(response))
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

