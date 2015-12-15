######################################################################################################################
#	install bundles helper unit
# A WebTools bund plugin					
#
#	Author: dane22, a Plex Community member
#
# This is to install/update a new channel from github into plex
# Also can return a list of already installed channels, as well as bundles avail on GitHub
######################################################################################################################

import datetime			# Used for a timestamp in the dict
#import json

class install(object):
	# Defaults used by the rest of the class
	def __init__(self):
		Log.Debug('******* Starting install *******')
		self.url = ''
		self.PLUGIN_DIR = Core.storage.join_path(Core.app_support_path, Core.config.bundles_dir_name)
		Log.Debug("Plugin directory is: %s" %(self.PLUGIN_DIR))

	''' Grap the tornado req, and process it '''
	def reqprocess(self, req):		
		function = req.get_argument('function', 'missing')
		if function == 'missing':
			req.clear()
			req.set_status(412)
			req.finish("<html><body>Missing function parameter</body></html>")
		elif function == 'getGit':
			url = req.get_argument('url', 'missing')
			if url == 'missing':
				req.clear()
				req.set_status(412)
				req.finish("<html><body>Missing url of git</body></html>")
			else:
				# Call install with the url
				self.install(url)	
				req.clear()
				req.set_status(200)
				req.finish("<html><body>All is cool</body></html>")
		elif function == 'list':
			return self.list(req)
		elif function == 'getLastUpdateTime':
			url = req.get_argument('url', 'missing')
			if url == 'missing':
				req.clear()
				req.set_status(412)
				req.finish("<html><body>Missing url of git</body></html>")
			return self.getLastUpdateTime(req, url)
		elif function == 'getListofBundles':
			return self.getListofBundles(req)
		else:
			req.clear()
			req.set_status(412)
			req.finish("<html><body>Unknown function call</body></html>")

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

	''' Download install/update from GitHub '''
	def install(self, url):
		# Get bundle name
		bundleName = self.grapBundleName(url)
		self.downloadBundle2tmp(url, bundleName)

	''' Grap bundle name '''
	def grapBundleName(self, url):		
		gitName = url.rsplit('/', 1)[-1]
		# Forgot to name git to end with .bundle?
		if not gitName.endswith('.bundle'):
			gitName = gitName + '.bundle'
		gitName = Core.storage.join_path(self.PLUGIN_DIR, gitName)
		Log.Debug('Bundle directory name digested as: %s' %(gitName))
		return gitName

	def getSavePath(self, plugin, path):
		fragments = path.split('/')[1:]
		# Remove the first fragment if it matches the bundle name
		if len(fragments) and fragments[0].lower() == plugin.lower():
			fragments = fragments[1:]
		return Core.storage.join_path(plugin, *fragments)

	''' Download the bundle '''
	def downloadBundle2tmp(self, url, bundleName):
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
			self.saveInstallInfo(url, bundleName)
		Log.Debug('Finished installing %s' %(bundleName))
		Log.Debug('******* Ending install *******')
		return 

	''' Save Install info to the dict '''
	def saveInstallInfo(self, url, bundleName):
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

	''' Get the last update time for a master branch '''
	def getLastUpdateTime(self, req, url):
		Log.Debug('Starting getLastUpdateTime')
		try:
			url += '/commits/master.atom'
			response = Datetime.ParseDate(HTML.ElementFromURL(url).xpath('//entry')[0].xpath('./updated')[0].text[:-6])
			Log.Debug('Last update for: ' + url + ' is: ' + str(response))
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
			url = 'https://api.github.com/repos/ukdtom/UAS2Res/contents/Resources/plugin_details.json?ref=master'
			responseJSON = JSON.ObjectFromURL(url)			
			response = responseJSON['content']
			response = String.Decode(response)
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






