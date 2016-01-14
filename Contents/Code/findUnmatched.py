######################################################################################################################
#	findUnmatched unit				
# A WebTools bundle plugin	
#
#	Author: dane22, a Plex Community member
#
#
######################################################################################################################

import urllib
import unicodedata
import json

class findUnmatched(object):
	# Defaults used by the rest of the class
	def __init__(self):
		Log.Debug('******* Starting findUnmatched *******')
		self.MovieChuncks = 20
		self.CoreUrl = 'http://127.0.0.1:32400/library/sections/'
		self.default_IGNORED_FILES = ['imdb.nfo', '.DS_Store', '__db.001', 'Thumbs.db', '.plexignore']
		self.default_IGNORED_DIRS = ['.@__thumb', '.AppleDouble', 'lost+found']
		self.default_VALID_EXTENSIONS = ['.m4v', '.3gp', '.nsv', '.ts', '.ty', '.strm', '.rm', '.rmvb', '.m3u',
																			'.mov', '.qt', '.divx', '.xvid', '.bivx', '.vob', '.nrg', '.img', '.iso', 
																			'.pva', '.wmv', '.asf', '.asx', '.ogm', '.m2v', '.avi', '.bin', '.dat', 
																			'.dvr-ms', '.mpg', '.mpeg', '.mp4', '.mkv', '.avc', '.vp3', '.svq3', '.nuv',
																			'.viv', '.dv', '.fli', '.flv', '.rar', '.001', '.wpl', '.zip', '.jpg', '.mp3']
		self.default_IGNORED_EXTENSIONS = ['.srt', '.xml', '.idx', '.jpg', '.sub', '.nfo', '.png', '.gif', '.txt', '.rtf',
																			'.m3u', '.rar', '.sfv', '.md5', '.ico', '.doc', '.zip', '.SRT2UTF-8']
		self.default_ALL_EXTENSIONS = False
		self.default_ENABLE_PLEXIGNORE = True
		self.default_IGNORE_HIDDEN = True

	''' Grap the tornado req, and process it '''
	def reqprocess(self, req):	
		function = req.get_argument('function', 'missing')
		if function == 'missing':
			req.clear()
			req.set_status(412)
			req.finish("<html><body>Missing function parameter</body></html>")
		elif function == 'scanSection':
			# Call scanSection with the url
			return self.scanSection(req)
		else:
			req.clear()
			req.set_status(412)
			req.finish("<html><body>Unknown function call</body></html>")

	''' Grap the tornado req, and process it for a PUT request'''
	def reqprocessPost(self, req):		
		function = req.get_argument('function', 'missing')
		if function == 'missing':
			req.clear()
			req.set_status(412)
			req.finish("<html><body>Missing function parameter</body></html>")
		elif function == 'setSettingstoDefault':
			return self.setSettingstoDefault(req)
		else:
			req.clear()
			req.set_status(412)
			req.finish("<html><body>Unknown function call</body></html>")

	# Save defaults to settings
	def setSettingstoDefault(self, req, internal = False):
		try:
			print 'Ged Set Settings to default'
			Log.Debug('findUnmatched set settings to default')
			defaults = {}
			defaults['IGNORED_FILES'] = self.default_IGNORED_FILES
			defaults['IGNORED_DIRS'] = self.default_IGNORED_DIRS
			defaults['VALID_EXTENSIONS'] = self.default_VALID_EXTENSIONS
			defaults['IGNORED_EXTENSIONS'] = self.default_IGNORED_EXTENSIONS
			defaults['ALL_EXTENSIONS'] = self.default_ALL_EXTENSIONS
			defaults['ENABLE_PLEXIGNORE'] = self.default_ENABLE_PLEXIGNORE
			defaults['IGNORE_HIDDEN'] = self.default_IGNORE_HIDDEN
			Dict['findUnmatched'] = defaults
			Dict.Save()
			req.clear()
			req.set_status(200)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish(json.dumps(Dict['findUnmatched']))
		except Exception, e:
			print 'GED Exception in setSettingstoDefault', str(e)
			Log.Debug('Fatal error happened in setSettingstoDefault: ' + str(e))
			req.clear()
			req.set_status(500)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish('Fatal error happened in getUpdateList: ' + str(e))


	# Main call for function.....
	def scanSection(self, req):

		# Scan the file system
		def getFiles(filePath):
			try:

				Log.Debug('******* Starting getFiles with a path of %s ***********' %(filePath))
				print 'GED ******* Starting getFiles with a path of %s ***********' %(filePath)
				scannedFiles = []
				
				# Check if Ignored files setting has been populated yet
				print 'GED findUnmatched-IGNORED_FILES', Dict['findUnmatched-IGNORED_FILES']
				if Dict['findUnmatched-IGNORED_FILES'] == None:
					Dict['findUnmatched-IGNORED_FILES'] = self.default_IGNORED_FILES
						



				return []


			except Exception, e:
				print 'GED Exception', str(e)




		# Get a list of all files in a Movie Library
		def scanMovieDb(sectionNumber):
			try:
				mediasFromDB = []
				Log.Debug('Starting scanMovieDb for section %s' %(sectionNumber))
#				# Start by getting the totals of this section			
#				totalSize = XML.ElementFromURL(self.CoreUrl + sectionNumber + '/all?X-Plex-Container-Start=1&X-Plex-Container-Size=0').get('totalSize')
#				Log.Debug('Total size of medias are %s' %(totalSize))
				# So let's walk the library
				iStart = 1
				while True:
					# Grap a chunk from the server
					medias = XML.ElementFromURL(self.CoreUrl + sectionNumber + '/all?X-Plex-Container-Start=' + str(iStart) + '&X-Plex-Container-Size=' + str(self.MovieChuncks)).xpath('//Part')
					# Walk the chunk
					for part in medias:						
#						iCurrent += 1
						filename = part.get('file')						
						filename = urllib.quote(unicodedata.normalize('NFKC', urllib.unquote(filename).decode('utf8')).encode('utf8'))
						# Remove esc backslash if present and on Windows
						if Platform.OS == "Windows":
							filename = filename.replace(':%5C%5C', ':%5C')
						mediasFromDB.append(filename)
					iStart += self.MovieChuncks
					if len(medias) == 0:
						break
				return mediasFromDB
			except Exception, e:
				Log.Debug('Fatal error in scanMovieDb: ' + str(e))
		# End scanMovieDb

# ************ Main function ************ 
		Log.Debug('scanSection started')
		try:
			# Grap the section number from the req
			sectionNumber = req.get_argument('section', 'missing')
			if sectionNumber == 'missing':
				req.clear()
				req.set_status(412)
				req.finish("<html><body>Missing section parameter</body></html>")
			# Let's find out the info of section here			
			response = XML.ElementFromURL(self.CoreUrl).xpath('//Directory[@key=' + sectionNumber + ']')
			sectionTitle = response[0].get('title')
			sectionType = response[0].get('type')
			locations = response[0].xpath('//Directory[@key=' + sectionNumber + ']/Location')
			sectionLocations = []
			for location in locations:
				sectionLocations.append(location.get('path'))
			Log.Debug('Going to scan section %s with a title of %s and a type of %s and locations as %s' %(sectionNumber, sectionTitle, sectionType, str(sectionLocations)))

			if sectionType == 'movie':
				filesFromDatabase = scanMovieDb(sectionNumber)


#			print 'GED filesFromDatabase:', filesFromDatabase
			print 'GED number', len(filesFromDatabase)
			Log.Debug('************** Files from database *****************')
			Log.Debug(filesFromDatabase)
			Log.Debug('************** Files from database end *************')


			# Now grap files from the filesystem
			filesFromFileSystem = []
			for filePath in sectionLocations:
				filesFromFileSystem.extend(getFiles(filePath))



		except Exception, e:
			Log.Debug('Fatal error happened in scanSection: ' + str(e))
			req.clear()
			req.set_status(500)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish('Fatal error happened in scanSection: ' + str(e))
			return req

