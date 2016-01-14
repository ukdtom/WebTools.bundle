######################################################################################################################
#	log files helper unit				
# A WebTools bundle plugin	
#
#	Author: dane22, a Plex Community member
#
#
######################################################################################################################
import shutil
import time
import json
import os
import zipfile

class logs(object):
	# Defaults used by the rest of the class
	def __init__(self):
		# Check if Log directory has been overwritten
		try:
			self.LOGDIR = os.environ['PLEX_MEDIA_SERVER_LOG_DIR']
		except:
			self.LOGDIR = os.path.join(Core.app_support_path, 'Logs')
		Log.Debug('Log Root dir is: ' + self.LOGDIR)

	''' Grap the tornado req for a Get, and process it '''
	def reqprocess(self, req):		
		function = req.get_argument('function', 'missing')
		if function == 'missing':
			req.clear()
			req.set_status(412)
			req.finish("<html><body>Missing function parameter</body></html>")
		elif function == 'list':
			return self.list(req)
		elif function == 'show':
			return self.show(req)
		elif function == 'download':
			return self.download(req)
		else:
			req.clear()
			req.set_status(412)
			req.finish("<html><body>Unknown function call</body></html>")

	''' Grap the tornado req, and process it '''
	def reqprocessPost(self, req):		
		function = req.get_argument('function', 'missing')
		if function == 'missing':
			req.clear()
			req.set_status(412)
			req.finish("<html><body>Missing function parameter</body></html>")
		elif function == 'entry':
			return self.entry(req)
		else:
			req.clear()
			req.set_status(412)
			req.finish("<html><body>Unknown function call</body></html>")


	#********** Functions below ******************

	''' This metode will add an entry to the logfile. '''
	def entry(self, req):
		Log.Debug('Starting Logs.entry function')
		try:
			text = req.get_argument('text', '')
			Log.Debug('FrontEnd: ' + text)
			req.clear()
			req.set_status(200)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish('Entry logged')
		except:
			Log.Debug('Fatal error happened in Logs entry')
			req.clear()
			req.set_status(500)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish('Fatal error happened in Logs entry')

	''' This metode will return a list of logfiles. accepts a filter parameter '''
	def list(self, req):
		Log.Debug('Starting Logs.List function')
		try:
			fileFilter = req.get_argument('filter', '')
			retFiles = []
			Log.Debug('List logfiles called for directory %s' %(self.LOGDIR))
			for root, dirs, files in os.walk(self.LOGDIR, topdown=True):
				# Only list from the default directories
				dirs[:] = [d for d in dirs if d in ['PMS Plugin Logs']]
				path = root.split('/')
				for filename in files:
					if fileFilter != '':
						if fileFilter.upper() in filename.upper():
							retFiles.append(filename)
					else:
						retFiles.append(filename)
			Log.Debug('Returning %s' %retFiles)		
			req.clear()
			req.set_status(200)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish(json.dumps(sorted(retFiles)))
		except:
			Log.Debug('Fatal error happened in Logs list')
			req.clear()
			req.set_status(500)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish('Fatal error happened in Logs list')

	''' This will return contents of the logfile as an array. Req. a parameter named fileName '''
	def show(self, req):
		try:
			fileName = req.get_argument('fileName', 'missing')
			Log.Debug('About to show log named: %s' %(fileName))
			if fileName == 'missing':
				req.clear()
				req.set_status(412)
				req.finish("<html><body>Missing fileName of log to show</body></html>")
				return req
			if 'com.plexapp' in fileName:
				file = os.path.join(self.LOGDIR, 'PMS Plugin Logs', fileName)
			else:
				file = os.path.join(self.LOGDIR, fileName)
			retFile = []
			with io.open(file, 'rb') as content_file:
				content = content_file.readlines()
				for line in content:
					line = line.replace('\n', '')
					line = line.replace('\r', '')
					retFile.append(line)
			req.clear()
			req.set_status(200)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish(json.dumps(retFile))
			return req
		except:
			Log.Debug('Fatal error happened in Logs show')
			req.clear()
			req.set_status(500)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish('Fatal error happened in Logs show')

	''' This will download a zipfile with the complete log directory. if parameter fileName is specified, only that file will be downloaded, and not zipped'''
	def download(self, req):
		try:
			fileName = req.get_argument('fileName', 'missing')
			Log.Debug('About to download logs and fileName param is: %s' %(fileName))
			if fileName == 'missing':
				# Need to download entire log dir as a zip			
				# Get current date and time, and add to filename
				downFile = 'PMSLogs_' + time.strftime("%Y%m%d-%H%M%S") + '.zip'
				zipFileName = 'PMSLogs.zip'
				myZip = zipfile.ZipFile(zipFileName, 'w')
				for root, dirs, files in os.walk(self.LOGDIR, topdown=True):
					# Only zip from the default directories
					dirs[:] = [d for d in dirs if d in ['PMS Plugin Logs']]
					for filename in files:
						fullFileName = os.path.join(root, filename)
						param, value = fullFileName.split(self.LOGDIR,1)
						myZip.write(os.path.join(root, filename), arcname=value)
				myZip.close()
				req.set_header('Content-Type', 'application/force-download')
				req.set_header ('Content-Disposition', 'attachment; filename=' + downFile)
				with io.open(zipFileName, 'rb') as f:
					try:
						while True:
							fbuffer = f.read(4096)
							if fbuffer:
								req.write(fbuffer)
							else:
								f.close()
								req.finish()
								# remove temp zip file again
								os.remove(zipFileName)
								return req
					except Exception, e:
						Log.Debug('Fatal error happened in Logs download: ' + str(e))
						req.clear()
						req.set_status(500)
						req.set_header('Content-Type', 'application/json; charset=utf-8')
						req.finish('Fatal error happened in Logs download: ' + str(e))
			else:
				try:
					if 'com.plexapp' in fileName:
						file = os.path.join(self.LOGDIR, 'PMS Plugin Logs', fileName)
					else:
						file = os.path.join(self.LOGDIR, fileName)
					retFile = []
					with io.open(file, 'rb') as content_file:
						content = content_file.readlines()
						for line in content:
							line = line.replace('\n', '')
							line = line.replace('\r', '')
							retFile.append(line)
					req.set_header('Content-Type', 'application/force-download')
					req.set_header ('Content-Disposition', 'attachment; filename=' + fileName)
					for line in retFile:
						req.write(line + '\n')
					req.finish()
					return req
				except Exception, e:
					Log.Debug('Fatal error happened in Logs download: ' + str(e))
					req.clear()
					req.set_status(500)
					req.set_header('Content-Type', 'application/json; charset=utf-8')
					req.finish('Fatal error happened in Logs download: ' + str(e))			
		except Exception, e:
			Log.Debug('Fatal error happened in Logs download: ' + str(e))
			req.clear()
			req.set_status(500)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish('Fatal error happened in Logs download: ' + str(e))

