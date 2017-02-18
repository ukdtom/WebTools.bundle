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
import io, os, shutil, sys
import plistlib
import pms
import tempfile
from consts import DEBUGMODE, UAS_URL, UAS_BRANCH, NAME, WTURL

class git(object):
	init_already = False							# Make sure part of init only run once

	# Init of the class
	def __init__(self):
		self.url = ''
		self.PLUGIN_DIR = Core.storage.join_path(Core.app_support_path, Core.config.bundles_dir_name)
		self.IGNORE_BUNDLE = ['WebTools.bundle', 'SiteConfigurations.bundle', 'Services.bundle']
		self.OFFICIAL_APP_STORE = 'https://nine.plugins.plexapp.com'


		# Only init this part once during the lifetime of this
		if not git.init_already:
			git.init_already = True
			Log.Debug('******* Starting git *******')
			Log.Debug("Plugin directory is: %s" %(self.PLUGIN_DIR))
			# See a few times, that the json file was missing, so here we check, and if not then force a download
			try:
				jsonFileName = Core.storage.join_path(self.PLUGIN_DIR, NAME + '.bundle', 'http', 'uas', 'Resources', 'plugin_details.json')
				if not os.path.isfile(jsonFileName):
					Log.Critical('UAS dir was missing the json, so doing a forced download here')
					self.updateUASCache(None, cliForce = True)
			except Exception, e:
				Log.Exception('Exception happend when trying to force download from UASRes: ' + str(e))
		
	''' Grap the tornado req, and process it for GET request'''
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
		elif function == 'upgradeWT':
			return self.upgradeWT(req)
		else:
			req.clear()
			req.set_status(412)
			req.finish("<html><body>Unknown function call</body></html>")

	''' Upgrade WebTools itself '''
	def upgradeWT(self, req):
		Log.Info('Starting upgradeWT')

		#Helper function
		''' This helper function will delete the dict named Installed
				After doing so, it'll do a forced migrate
		'''
		def nukeSpecialDicts():
			#TODO Make this
			Dict['installed'] = {}
			Dict.Save()
			self.migrate(req, silent=True)

		# Helper function
		def removeEmptyFolders(path, removeRoot=True):
			'Function to remove empty folders'
			if not os.path.isdir(path):
				return
			# remove empty subfolders
			files = os.listdir(path)
			if len(files):
				for f in files:
					fullpath = os.path.join(path, f)
					if os.path.isdir(fullpath):
						removeEmptyFolders(fullpath)
			# if folder empty, delete it
			files = os.listdir(path)
			if len(files) == 0 and removeRoot:
				Log.Debug('Removing empty directory: ' + path)
				os.rmdir(path)

		# Reset dicts
		nukeSpecialDicts()

		url= req.get_argument('debugURL', WTURL)
		bundleName = Core.storage.join_path(Core.app_support_path, Core.config.bundles_dir_name, NAME + '.bundle')
		Log.Info('WT install dir is: ' + bundleName)
		try:
			if 'https://api.github.com/repos/' in url:
				Log.Debug('Getting release info from url: ' + url)
				jsonReponse = JSON.ObjectFromURL(url)
				# Walk assets to find the one named WebTools.bundle.zip
				for asset in jsonReponse['assets']:
					if asset['name'] == 'WebTools.bundle.zip':
						wtURL = asset['browser_download_url']					
			else:
				wtURL = url.replace('tree', 'archive') + '.zip'
			Log.Info('WT Download url detected as: ' + wtURL)
			# Grap file from Github
			zipfile = Archive.ZipFromURL(wtURL)
			bError = True
			bUpgrade = False
			instFiles = []
			# We need to cut of the main directory, which name we don't know
			for filename in zipfile:
				pos = filename.find('/')
				cutStr = filename[:pos]
				break
			# Now build a list of files in the zip, while extracting them as well
			for filename in zipfile:
				myFile = filename.replace(cutStr, '')
				if myFile != '/':
					# Make a list of all files and dirs in the zip
					instFiles.append(myFile)
				# Grap the file
				data = zipfile[filename]
				if not str(filename).endswith('/'):
					# Pure file, so save it	
					path = self.getSavePath(bundleName, filename.replace(cutStr, ''))
					Log.Debug('Extracting file' + path)
					try:
						Core.storage.save(path, data)
					except Exception, e:
						bError = True
						Log.Exception('Exception happend in downloadBundle2tmp: ' + str(e))
				else:
					# We got a directory here
					Log.Debug(filename.split('/')[-2])
					if not str(filename.split('/')[-2]).startswith('.'):
						# Not hidden, so let's create it
						path = self.getSavePath(bundleName, filename.replace(cutStr, ''))
						Log.Debug('Extracting folder ' + path)
						try:
							Core.storage.ensure_dirs(path)
						except Exception, e:
							bError = True
							Log.Exception('Exception happend in downloadBundle2tmp: ' + str(e))
			# Now we need to nuke files that should no longer be there!
			for root, dirs, files in os.walk(bundleName):
				for fname in files:
					fileName = Core.storage.join_path(root, fname).replace(bundleName, '')
					if fileName not in instFiles:
						if 'uas' not in fileName:
							Log.Debug('Removing not needed file: ' + fileName)
							os.remove(Core.storage.join_path(root, fname))
			# And now time to swipe empty directories
			removeEmptyFolders(bundleName)

			req.clear()
			req.set_status(200)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish('Upgraded ok')
		except Exception, e:
			Log.Critical('***************************************************************')
			Log.Critical('Error when updating WebTools')
			Log.Critical('***************************************************************')
			Log.Critical('DARN....When we tried to upgrade WT, we had an error :-(')
			Log.Critical('Only option now might be to do a manual install, like you did the first time')
			Log.Critical('Do NOT FORGET!!!!')
			Log.Critical('We NEED this log, so please upload to Plex forums')
			Log.Critical('***************************************************************')
			Log.Exception('The error was: ' + str(e))
		return

	''' Returns commit time and Id for a git branch '''
	def getAtom_UpdateTime_Id(self, url, branch):		
		try:
			# Build AtomUrl
			atomUrl = url + '/commits/' + branch + '.atom'
			# Get Atom
			atom = HTML.ElementFromURL(atomUrl)
			mostRecent = atom.xpath('//entry')[0].xpath('./updated')[0].text[:-6]
			commitId = atom.xpath('//entry')[0].xpath('./id')[0].text.split('/')[-1][:10]
		except Exception, e:
			commitId = '0'
			mostRecent = 'Not found'
			pass
		return {'commitId' : commitId, 'mostRecent' : mostRecent}

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
						# Going the new detection way with the commitId?
						if 'CommitId' in Dict['installed'][bundle]:	
							if 'release' in Dict['installed'][bundle]:								
								relUrl = 'https://api.github.com/repos' + bundle[18:] + '/releases/latest'
								Id = JSON.ObjectFromURL(relUrl)['id']
								if Dict['installed'][bundle]['CommitId'] != Id:
									gitInfo = Dict['installed'][bundle]
									gitInfo['gitHubTime'] = JSON.ObjectFromURL(relUrl)['published_at']
									result[bundle] = gitInfo
							else:
								updateInfo = self.getAtom_UpdateTime_Id(bundle, Dict['installed'][bundle]['branch'])
								if Dict['installed'][bundle]['CommitId'] != updateInfo['commitId']:
									gitInfo = Dict['installed'][bundle]
									gitInfo['gitHubTime'] = updateInfo['mostRecent']
									result[bundle] = gitInfo
						else:
							# Sadly has to use timestamps							
							Log.Info('Using timestamps to detect avail update for ' + bundle)
							gitTime = datetime.datetime.strptime(self.getLastUpdateTime(req, UAS=True, url=bundle), '%Y-%m-%d %H:%M:%S')
							sBundleTime = Dict['installed'][bundle]['date']
							bundleTime = datetime.datetime.strptime(sBundleTime, '%Y-%m-%d %H:%M:%S')
							# Fix for old stuff, where branch was empty
							if Dict['installed'][bundle]['branch'] == '':
								Dict['installed'][bundle]['branch'] = 'master'
								Dict.Save()
							if bundleTime < gitTime:
								gitInfo = Dict['installed'][bundle]
								gitInfo['gitHubTime'] = str(gitTime)
								result[bundle] = gitInfo
							else:
								# Let's get a CommitId stamped for future times								
								updateInfo = self.getAtom_UpdateTime_Id(bundle, Dict['installed'][bundle]['branch'])
								Log.Info('Stamping %s with a commitId of %s for future ref' %(bundle, updateInfo['commitId']))							
								Dict['installed'][bundle]['CommitId'] = updateInfo['commitId']
								Dict.Save()
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
			Log.Exception('Fatal error happened in getUpdateList: ' + str(e))
			req.clear()
			req.set_status(500)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish('Fatal error happened in getUpdateList ' + str(e))

	''' This function will migrate bundles that has been installed without using our UAS into our UAS '''
	def migrate(self, req, silent=False):
		# get list from uas cache
		def getUASCacheList():
			try:
				Log.Info('Migrating old bundles into WT')
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
				Log.Exception('Exception in Migrate/getUASCacheList : ' + str(e))
				return ''

		# Grap indentifier from plist file and timestamp
		def getIdentifier(pluginDir):
			try:
				pFile = Core.storage.join_path(self.PLUGIN_DIR, pluginDir, 'Contents', 'Info.plist')
				pl = plistlib.readPlist(pFile)
				createStamp = datetime.datetime.fromtimestamp(os.path.getmtime(pFile)).strftime('%Y-%m-%d %H:%M:%S')			
				return (pl['CFBundleIdentifier'], createStamp)
			except Exception, e:
				errMsg = str(e) + '\nfor something in directory: ' + Core.storage.join_path(self.PLUGIN_DIR, pluginDir)
				errMsg = errMsg + '\nSkipping migration of directory'
				Log.Error('Exception in Migrate/getIdentifier : ' + errMsg)				
				pass

		# Main call
		Log.Debug('Migrate function called')
		try:
			# Let's start by getting a list of known installed bundles
			knownBundles = []
			for installedBundles in Dict['installed']:
				knownBundles.append(Dict['installed'][installedBundles]['bundle'].upper())
			# Grap a list of directories in the plugin dir
			dirs = os.listdir(self.PLUGIN_DIR)
			migratedBundles = {}
			for pluginDir in dirs:
				if pluginDir.endswith('.bundle'):
					if not pluginDir.startswith('.'):
						# It's a bundle
						if pluginDir.upper() not in knownBundles:
							# It's unknown
							if pluginDir not in self.IGNORE_BUNDLE:
								Log.Debug('About to migrate %s' %(pluginDir))
								# This we need to migrate
								try:
									(target, dtStamp) = getIdentifier(pluginDir)
								except Exception, e:
									continue				
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
										targetGit['supporturl'] = uasListjson[git]['supporturl']
										Dict['installed'][git] = targetGit
										Log.Debug('Dict stamped with the following install entry: ' + git + ' - '  + str(targetGit))
										# Now update the PMS-AllBundleInfo Dict as well
										Dict['PMS-AllBundleInfo'][git] = targetGit
										# Update installed dict as well
										Dict['installed'][git] = targetGit
										# If it existed as unknown as well, we need to remove that
										Dict['PMS-AllBundleInfo'].pop(uasListjson[git]['identifier'], None)
										Dict['installed'].pop(uasListjson[git]['identifier'], None)										
										Dict.Save()
										migratedBundles[git] = targetGit
										bFound = True
										pms.updateUASTypesCounters()
										break
								if not bFound:
									Log.Debug('Found %s is sadly not part of uas' %(pluginDir))
									vFile = Core.storage.join_path(self.PLUGIN_DIR, pluginDir, 'Contents', 'VERSION')
									if os.path.isfile(vFile):
										Log.Debug(pluginDir + ' is an official bundle, so skipping')
									else:
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
										migratedBundles[target] = git
										Log.Debug('Dict stamped with the following install entry: ' + pluginDir + ' - '  + str(git))
										Dict.Save()
										pms.updateUASTypesCounters()
			Log.Debug('Migrated: ' + str(migratedBundles))
			if silent:
				return
			else:
				req.clear()
				req.set_status(200)
				req.set_header('Content-Type', 'application/json; charset=utf-8')
				req.finish(json.dumps(migratedBundles))
		except Exception, e:
			Log.Exception('Fatal error happened in migrate: ' + str(e))
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
			Log.Exception('Exception in uasTypes: ' + str(e))
			req.clear()
			req.set_status(500)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish('Fatal error happened in uasTypes: ' + str(e))
			return req

	''' This will update the UAS Cache directory from GitHub '''
	def updateUASCache(self, req, cliForce= False):
		Log.Debug('Starting to update the UAS Cache')
		if not cliForce:
			Force = ('false' != req.get_argument('Force', 'false'))
		else:
			Force = True
		# Main call
		try:
			# Start by getting the time stamp for the last update
			lastUpdateUAS = Dict['UAS']
			Log.Debug('Last update time for UAS Cache is: %s' %(lastUpdateUAS))
			if lastUpdateUAS == None:
				# Not set yet, so default to Linux start date
				lastUpdateUAS = datetime.datetime.strptime('01-01-1970 00:00:00', '%m-%d-%Y %H:%M:%S')
			else:
				lastUpdateUAS = datetime.datetime.strptime(str(lastUpdateUAS), '%Y-%m-%d %H:%M:%S.%f')
			# Now get the last update time from the UAS repository on GitHub
			masterUpdate = datetime.datetime.strptime(self.getLastUpdateTime(req, True, UAS_URL), '%Y-%m-%d %H:%M:%S')
			# Do we need to update the cache, and add 2 min. tolerance here?
			if ((masterUpdate - lastUpdateUAS) > datetime.timedelta(seconds = 120) or Force):
				# We need to update UAS Cache
				# Target Directory
				targetDir = Core.storage.join_path(self.PLUGIN_DIR, NAME + '.bundle', 'http', 'uas')
				# Force creation, if missing
				try:
					Core.storage.ensure_dirs(targetDir)
				except Exception, e:
					errMsg = str(e)
					if 'Errno 13' in errMsg:
						errMsg = errMsg + '\n\nLooks like permissions are not correct, cuz we where denied access\n'
						errMsg = errMsg + 'to create a needed directory.\n\n'
						errMsg = errMsg + 'If running on Linux, you might have to issue:\n'
						errMsg = errMsg + 'sudo chown plex:plex ./WebTools.bundle -R\n'
						errMsg = errMsg + 'And if on Synology, the command is:\n'
						errMsg = errMsg + 'sudo chown plex:users ./WebTools.bundle -R\n'
					Log.Exception('Exception in updateUASCache ' + errMsg)
					if not cliForce: 
						req.clear()
						req.set_status(500)
						req.set_header('Content-Type', 'application/json; charset=utf-8')
						req.finish('Exception in updateUASCache: ' + errMsg)
						return req
					else:
						return
				# Grap file from Github
				try:
					zipfile = Archive.ZipFromURL(UAS_URL+ '/archive/' + UAS_BRANCH + '.zip')							
				except Exception, e:
					Log.Exception('Could not download UAS Repo from GitHub'  + str(e))
					if not cliForce:
						req.clear()
						req.set_status(500)
						req.set_header('Content-Type', 'application/json; charset=utf-8')
						req.finish('Exception in updateUASCache while downloading UAS repo from Github: ' + str(e))
						return req					
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
							Log.Exception("Unexpected Error " + str(e))
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
								Log.Exception("Unexpected Error " + str(e))
				# Update the AllBundleInfo as well
				pms.updateAllBundleInfoFromUAS()
				pms.updateUASTypesCounters()
			else:
				Log.Debug('UAS Cache already up to date')
			# Set timestamp in the Dict
			Dict['UAS'] = datetime.datetime.now()
			if not cliForce:
				req.clear()
				req.set_status(200)
				req.set_header('Content-Type', 'application/json; charset=utf-8')
				req.finish('UASCache is up to date')	
		except Exception, e:
			Log.Exception('Exception in updateUASCache ' + str(e))
			if not cliForce:
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
				bundleInfo = Dict['PMS-AllBundleInfo'].get(url, {})

				if bundleInfo.get('bundle'):
					# Use bundle name from plugin details
					gitName = bundleInfo['bundle']
				else:
					# Fallback to just appending ".bundle" to the repository name
					gitName = gitName + '.bundle'

			gitName = Core.storage.join_path(self.PLUGIN_DIR, gitName)
			Log.Debug('Bundle directory name digested as: %s' %(gitName))
			return gitName

		''' Save Install info to the dict '''
		def saveInstallInfo(url, bundleName, branch):
			# If this is WebTools itself, then don't save
			if 'WebTools.bundle' in bundleName:
				return

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
					# Needs to seperate between release downloads, and branch downloads
					if 'RELEASE' in branch.upper():
						relUrl = 'https://api.github.com/repos' + url[18:] + '/releases/latest'
						Id = JSON.ObjectFromURL(relUrl)['id']
					else:
						Id = HTML.ElementFromURL(url + '/commits/' + branch + '.atom').xpath('//entry')[0].xpath('./id')[0].text.split('/')[-1][:10]
					key = git['repo']
					del git['repo']
					git['CommitId'] = Id
					git['branch'] = branch
					git['date'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
					Dict['installed'][key] = git
					bNotInUAS = False
					Log.Debug('Dict stamped with the following install entry: ' + key + ' - '  + str(git))
					# Now update the PMS-AllBundleInfo Dict as well
					Dict['PMS-AllBundleInfo'][key] = git
					pms.updateUASTypesCounters()
					break
			if bNotInUAS:
				key = url
				# Get the last Commit Id of the branch
				Id = HTML.ElementFromURL(url + '/commits/master.atom').xpath('//entry')[0].xpath('./id')[0].text.split('/')[-1][:10]
				pFile = Core.storage.join_path(self.PLUGIN_DIR, bundleName, 'Contents', 'Info.plist')
				pl = plistlib.readPlist(pFile)
				git = {}
				git['CommitId'] = Id
				git['title'] = os.path.basename(bundleName)[:-7]
				git['description'] = ''
				git['branch'] = branch
				git['bundle'] = os.path.basename(bundleName)
				git['identifier'] = pl['CFBundleIdentifier']
				git['type'] = ['Unknown']
				git['icon'] = ''
				git['date'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
				Dict['installed'][key] = git
				# Now update the PMS-AllBundleInfo Dict as well
				Dict['PMS-AllBundleInfo'][key] = git
				Log.Debug('Dict stamped with the following install entry: ' + key + ' - '  + str(git))
				pms.updateUASTypesCounters()
			Dict.Save()
			return

		''' Get latest Release version '''
		def getLatestRelease(url):
			# Get release info if present
			try:
				relUrl = 'https://api.github.com/repos' + url[18:] + '/releases/latest'
				relInfo = JSON.ObjectFromURL(relUrl)
				downloadUrl = None
				for asset in relInfo['assets']:
					if asset['name'].upper() == Dict['PMS-AllBundleInfo'][url]['release'].upper():
						downloadUrl = asset['browser_download_url']
						continue	
				if downloadUrl:
					return downloadUrl
				else:
					raise "Download URL not found"
			except Exception, ex:
				Log.Critical('Release info not found on Github: ' + relUrl)
				pass			
			return

		''' Download the bundle '''
		def downloadBundle2tmp(url, bundleName, branch):
			# Helper function
			def removeEmptyFolders(path, removeRoot=True):
				'Function to remove empty folders'
				if not os.path.isdir(path):
					return
				# remove empty subfolders
				files = os.listdir(path)
				if len(files):
					for f in files:
						fullpath = os.path.join(path, f)
						if os.path.isdir(fullpath):
							removeEmptyFolders(fullpath)
				# if folder empty, delete it
				files = os.listdir(path)
				if len(files) == 0 and removeRoot:
					Log.Debug('Removing empty directory: ' + path)
					os.rmdir(path)

			try:
				# Get the dict with the installed bundles, and init it if it doesn't exists
				if not 'installed' in Dict:
					Dict['installed'] = {}
				if 'RELEASE' in branch.upper():
					zipPath = getLatestRelease(url)
				else:
					zipPath = url + '/archive/' + branch + '.zip'
				try:
					# Grap file from Github
					zipfile = Archive.ZipFromURL(zipPath)
				except Exception, e:
					Log.Exception('Exception in downloadBundle2tmp while downloading from GitHub: ' + str(e))
					return False
				# Create base directory
				Core.storage.ensure_dirs(Core.storage.join_path(self.PLUGIN_DIR, bundleName))
				# Make sure it's actually a bundle channel
				bError = True
				bUpgrade = False
				try:
					for filename in zipfile:
						if '/Contents/Info.plist' in filename:
							pos = filename.find('/Contents/')
							cutStr = filename[:pos]
							bError = False
							# so we hit the Info.plist file, and now we can make sure, that/if this is an upgrade or not
							# So let's grap the identifier from the info file	of the bundle to be migrated	
							# We start by temporary save that as Plug-ins/WT-tmp.plist
							Core.storage.save(self.PLUGIN_DIR + '/WT-tmp.plist', zipfile[filename])
							# Now read out the identifier
							bundleId = plistlib.readPlist(self.PLUGIN_DIR + '/WT-tmp.plist')['CFBundleIdentifier']
							Log.Debug('Identifier of the bundle to be installed is: ' + bundleId)
							# Then nuke the file again
							os.remove(self.PLUGIN_DIR + '/WT-tmp.plist')
							# And finally check if it's already installed
							for bundle in Dict['installed']:
								if Dict['installed'][bundle]['identifier'] == bundleId:
									bUpgrade = True
									Log.Debug('Install is an upgrade')
									break
				except Exception, e:
					Log.Exception('Exception in downloadBundle2tmp while walking the downloaded file to find the plist: ' + str(e))
					return False					
				if bUpgrade:
					# Since this is an upgrade, we need to check, if the dev wants us to delete the Cache directory
					if url in Dict['installed'].keys():
						CacheDir = Core.storage.join_path(Core.app_support_path, 'Plug-in Support', 'Caches', bundleId)
						if 'DeleteCacheDir' in Dict['PMS-AllBundleInfo'][url]:
							if Dict['PMS-AllBundleInfo'][url]['DeleteCacheDir']:
								Log.Info('Deleting the Cache directory ' + CacheDir)
								shutil.rmtree(CacheDir)
							else:
								Log.Info('Keeping the Cache directory ' + CacheDir)
					# Since this is an upgrade, we need to check, if the dev wants us to delete the Data directory
					if url in Dict['installed'].keys():
						DataDir = Core.storage.join_path(Core.app_support_path, 'Plug-in Support', 'Data', bundleId)
						if 'DeleteDataDir' in Dict['PMS-AllBundleInfo'][url]:
							if Dict['PMS-AllBundleInfo'][url]['DeleteDataDir']:
								Log.Info('Deleting the Data directory ' + DataDir)
								shutil.rmtree(DataDir)
							else:
								Log.Info('Keeping the Data directory ' + DataDir)

				if bError:
					Core.storage.remove_tree(Core.storage.join_path(self.PLUGIN_DIR, bundleName))
					Log.Debug('The bundle downloaded is not a Plex Channel bundle!')
					raise ValueError('The bundle downloaded is not a Plex Channel bundle!')
				bError = False
				if not bUpgrade:
					presentFiles = []

				# Create temporary directory
				tempDir = tempfile.mkdtemp(prefix='wt-')
				extractDir = os.path.join(tempDir, os.path.basename(bundleName))

				Log.Info('Extracting plugin to: %r', extractDir)

				# Extract archive into temporary directory
				for filename in zipfile:
					data = zipfile[filename]

					if not str(filename).endswith('/'):
						if cutStr not in filename:
							continue

						# Pure file, so save it	
						path = extractDir + filename.replace(cutStr, '')
						Log.Debug('Extracting file: ' + path)
						try:
							Core.storage.save(path, data)
						except Exception, e:
							bError = True
							Log.Exception('Exception happend in downloadBundle2tmp: ' + str(e))
					else:
						if cutStr not in filename:
							continue

						# We got a directory here
						Log.Debug(filename.split('/')[-2])
						if not str(filename.split('/')[-2]).startswith('.'):
							# Not hidden, so let's create it
							path = extractDir + filename.replace(cutStr, '')
							Log.Debug('Extracting folder: ' + path)
							try:
								Core.storage.ensure_dirs(path)
							except Exception, e:
								bError = True
								Log.Exception('Exception happend in downloadBundle2tmp: ' + str(e))

				if not bError and bUpgrade:
					# Copy files that should be kept between upgrades ("keepFiles")
					keepFiles = Dict['PMS-AllBundleInfo'].get(url, {}).get('keepFiles', [])

					for filename in keepFiles:
						sourcePath = bundleName + filename

						if not os.path.exists(sourcePath):
							Log.Debug('File does not exist: %r', sourcePath)
							continue

						destPath = extractDir + filename

						Log.Debug('Copying %r to %r', sourcePath, destPath)

						# Ensure directories exist
						destDir = os.path.dirname(destPath)

						try:
							Core.storage.ensure_dirs(destDir)
						except Exception, e:
							Log.Warn('Unable to create directory: %r - %s', destDir, e)
							continue

						# Copy file into temporary directory
						try:
							shutil.copy2(sourcePath, destPath)
						except Exception, e:
							Log.Warn('Unable to copy file to: %r - %s', destPath, e)
							continue

					# Remove any empty directories in plugin
					removeEmptyFolders(extractDir)

				if not bError:
					try:
						# Delete current plugin
						if os.path.exists(bundleName):
							Log.Info('Deleting %r', bundleName)
							shutil.rmtree(bundleName)

						# Move updated bundle into "Plug-ins" directory
						Log.Info('Moving %r to %r', extractDir, bundleName)
						shutil.move(extractDir, bundleName)
					except Exception, e:
						bError = True
						Log.Exception('Unable to update plugin: ' + str(e))

					# Delete temporary directory
					try:
						shutil.rmtree(tempDir)
					except Exception, e:
						Log.Warn('Unable to delete temporary directory: %r - %s', tempDir, e)

				if not bError:
					# Install went okay, so save info
					saveInstallInfo(url, bundleName, branch)
					# Install went okay, so let's make sure it get's registred
					if bUpgrade:
						try:
							pFile = Core.storage.join_path(self.PLUGIN_DIR, bundleName, 'Contents', 'Info.plist')
							pl = plistlib.readPlist(pFile)
							HTTP.Request('http://127.0.0.1:32400/:/plugins/%s/restart' % pl['CFBundleIdentifier'], cacheTime=0, immediate=True)
						except:
							try:
								HTTP.Request('http://127.0.0.1:32400/:/plugins/com.plexapp.system/restart', immediate=True)
							except:
								pass
					else:
						try:
							HTTP.Request('http://127.0.0.1:32400/:/plugins/com.plexapp.system/restart', immediate=True)
						except:
							pass
					return True
			except Exception, e:
				Log.Exception('Exception in downloadBundle2tmp: ' + str(e))
				return False

		# Starting install main
		Log.Debug('Starting install')
		req.clear()
		url = req.get_argument('url', 'missing')
		# Set branch to url argument, or master if missing
		branch = req.get_argument('branch', 'master')
		# Got a release url, and if not, go for what's in the dict for branch
		try:
			branch = Dict['PMS-AllBundleInfo'][url]['release']+'_WTRELEASE'
		except:
			try:
				branch = Dict['PMS-AllBundleInfo'][url]['branch']
			except:
				pass
		if url == 'missing':
			req.set_status(412)
			req.finish("<html><body>Missing url of git</body></html>")
			return req
		# Get bundle name
		bundleName = grapBundleName(url)
		if downloadBundle2tmp(url, bundleName, branch):
			Log.Debug('Finished installing %s from branch %s' %(bundleName, branch))
			Log.Debug('******* Ending install *******')
			req.clear()
			req.set_status(200)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish('All is cool')
			return req
		else:
			Log.Critical('Fatal error happened in install for :' + url)
			req.set_status(500)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish('Fatal error happened in install for :' + url + ' with branch ' + branch)
			return req

	''' Get the last update time for a master branch. if UAS is set to True, then this is an internal req. for UAS '''
	def getLastUpdateTime(self, req, UAS=False, url=''):
		Log.Debug('Starting getLastUpdateTime')
		# Wanted to internally check for UAS update?
		if not UAS:			
			url = req.get_argument('url', 'missing')
		if url == 'missing':
			req.clear()
			req.set_status(412)
			req.finish("<html><body>Missing url of git</body></html>")
			return req
		if not url.startswith('http'):
			req.clear()
			req.set_status(404)
			req.finish("<html><body>Missing url of git</body></html>")
			return req
		# Retrieve current branch name
		if Dict['installed'].get(url, {}).get('branch'):
			# Use installed branch name
			branch = Dict['installed'][url]['branch']
		elif Dict['PMS-AllBundleInfo'].get(url, {}).get('branch'):
			# Use branch name from bundle info
			branch = Dict['PMS-AllBundleInfo'][url]['branch']
		# UAS branch override ?
		elif url == UAS_URL :
			branch = UAS_BRANCH
		else:
			# Otherwise fallback to the "master" branch
			branch = 'master'
		# Check for updates
		try:
			if '_WTRELEASE' in branch:
				url = 'https://api.github.com/repos' + url[18:] + '/releases/latest'
				Log.Debug('URL is: ' + url)				
				response = JSON.ObjectFromURL(url)['published_at']
			else:
				url += '/commits/%s.atom' % branch
				Log.Debug('URL is: ' + url)
				response = Datetime.ParseDate(HTML.ElementFromURL(url).xpath('//entry')[0].xpath('./updated')[0].text).strftime("%Y-%m-%d %H:%M:%S")
			Log.Debug('Last update for: ' + url + ' is: ' + str(response))
			if UAS:
				return response
			else:
				req.clear()
				req.set_status(200)
				req.set_header('Content-Type', 'application/json; charset=utf-8')
				req.finish(str(response))
		except Exception, e:
			Log.Exception('Fatal error happened in getLastUpdateTime for :' + url +  ' was: ' + str(e))
			req.clear()
			req.set_status(500)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish('Fatal error happened in getLastUpdateTime for :' + url +  ' was: ' + str(e))

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
			Log.Critical('Fatal error happened in getListofBundles')
			req.clear()
			req.set_status(500)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish('Fatal error happened in getListofBundles')

	''' Get release info for a bundle '''
	def getReleaseInfo(self, req):
		Log.Info('Starting getReleaseInfo')
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
			Log.Critical('Fatal error happened in getReleaseInfo')
			req.clear()
			req.set_status(500)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish('Fatal error happened in getInfo')

