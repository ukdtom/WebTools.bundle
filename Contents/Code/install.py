######################################################################################################################
#	install bundles helper unit					
#
#	Author: dane22, a Plex Community member
#
# NAME variable must be defined in the calling unit, and is the name of the application
#
# This is to install/update a new channel from github into plex
######################################################################################################################

class install(object):
	# Defaults used by the rest of the class
	def __init__(self):
		Log.Debug('******* Starting install *******')
		self.PLUGIN_DIR = Core.storage.join_path(Core.app_support_path, Core.config.bundles_dir_name)
		Log.Debug("Plugin directory is: %s" %(self.PLUGIN_DIR))

	''' Download install/update from GitHub '''
	def install(self, url):
		# Convert url
		url = self.convertURL(url)
		# Get bundle name
		bundleName = self.grapBundleName(url)
		self.downloadBundle2tmp(url, bundleName)

	''' Convert url '''
	def convertURL(self, url):
		Log.Debug('Recieved install url as: %s' %url)
		url = url.replace("--wt--", "/")
		Log.Debug('Converted install url as: %s' %url)
		return url

	''' Grap bundle name '''
	def grapBundleName(self, url):
		gitName = url.rsplit('/', 1)[-1]
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
						Log.Debug("Unexpected Error")
		Log.Debug('Finished installing %s' %(bundleName))
		Log.Debug('******* Ending install *******')
		return









