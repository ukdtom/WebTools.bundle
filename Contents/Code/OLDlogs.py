######################################################################################################################
#	log files helper unit					
#
#	Author: dane22, a Plex Community member
#
# NAME variable must be defined in the calling unit, and is the name of the application
#
######################################################################################################################
import shutil

class OLDlogs(object):
	# Defaults used by the rest of the class
	def __init__(self):
		self.LOGDIR = os.path.join(Core.app_support_path, 'Logs')
	
	''' This metode will return a list of logfiles '''
	def list(self, filter=''):
		retFiles = []
		Log.Debug('List logfiles called for directory %s' %(self.LOGDIR))
		for root, dirs, files in os.walk(self.LOGDIR):
			path = root.split('/')
			for file in files:
				if filter != '':
					if filter in file:
						retFiles.append(file)
				else:
					retFiles.append(file)
		Log.Debug('Returning %s' %retFiles)
		return sorted(retFiles)

	''' This will return contents of the logfile as an array '''
	def show(self, fname):
		if 'com.plexapp' in fname:
			file = os.path.join(self.LOGDIR, 'PMS Plugin Logs', fname)
		else:
			file = os.path.join(self.LOGDIR, fname)
		retFile = []
		with io.open(file, 'rb') as content_file:
			content = content_file.readlines()
			for line in content:
				line = line.replace('\n', '')
				line = line.replace('\r', '')
				retFile.append(line)
		return retFile

	''' This will create a zipfile of the whole log directory, and return it '''
	def getAllAsZip(self):
		fileName = 'PMSLogs'
		myZip = shutil.make_archive(os.path.join(Core.app_support_path, fileName), 'zip', self.LOGDIR)
		return myZip


