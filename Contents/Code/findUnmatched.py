######################################################################################################################
#	findUnmatched unit				
# A WebTools bundle plugin	
#
#	Author: dane22, a Plex Community member
#
######################################################################################################################

import urllib
import unicodedata
import json

# Consts used here
AmountOfMediasInDatabase = 0				# Int of amount of medias in a database section

class findUnmatched(object):	
	# Defaults used by the rest of the class
	def __init__(self):
		Log.Debug('******* Starting findUnmatched *******')
		self.MovieChuncks = 20
		self.CoreUrl = 'http://127.0.0.1:32400/library/sections/'

	''' Populate the defaults, if not already there '''
	def populatePrefs(self):
		if Dict['FindUnmatched-default_ALL_EXTENSIONS'] == None:
			Dict['FindUnmatched-default_ALL_EXTENSIONS'] = False
		if Dict['FindUnmatched-default_ENABLE_PLEXIGNORE'] == None:
			Dict['FindUnmatched-default_ENABLE_PLEXIGNORE'] = True
		if Dict['FindUnmatched-default_IGNORE_HIDDEN'] == None:
			Dict['FindUnmatched-default_IGNORE_HIDDEN'] = True
		if Dict['FindUnmatched-default_IGNORED_FILES'] == None:
			Dict['FindUnmatched-default_IGNORED_FILES'] = ['imdb.nfo', '.DS_Store', '__db.001', 'Thumbs.db', '.plexignore']
		if Dict['FindUnmatched-default_IGNORED_DIRS'] == None:
			Dict['FindUnmatched-default_IGNORED_DIRS'] = ['.@__thumb', '.AppleDouble', 'lost+found']
		if Dict['FindUnmatched-default_VALID_EXTENSIONS'] == None:
			Dict['FindUnmatched-default_VALID_EXTENSIONS'] = ['.m4v', '.3gp', '.nsv', '.ts', '.ty', '.strm', '.rm', '.rmvb', '.m3u',
																			'.mov', '.qt', '.divx', '.xvid', '.bivx', '.vob', '.nrg', '.img', '.iso', 
																			'.pva', '.wmv', '.asf', '.asx', '.ogm', '.m2v', '.avi', '.bin', '.dat', 
																			'.dvr-ms', '.mpg', '.mpeg', '.mp4', '.mkv', '.avc', '.vp3', '.svq3', '.nuv',
																			'.viv', '.dv', '.fli', '.flv', '.rar', '.001', '.wpl', '.zip', '.jpg', '.mp3']
		if Dict['FindUnmatched-default_IGNORED_EXTENSIONS'] == None:
			Dict['FindUnmatched-default_IGNORED_EXTENSIONS'] = ['.srt', '.xml', '.idx', '.jpg', '.sub', '.nfo', '.png', '.gif', '.txt', '.rtf',
																			'.m3u', '.rar', '.sfv', '.md5', '.ico', '.doc', '.zip', '.SRT2UTF-8']

	''' Grap the tornado req, and process it '''
	def reqprocess(self, req):	
		function = req.get_argument('function', 'missing')
		if function == 'missing':
			req.clear()
			req.set_status(412)
			req.finish("Missing function parameter")
		elif function == 'scanSection':
			# Call scanSection with the url
			return self.scanSection(req)
		elif function == 'getStatus':
			# Call scanSection with the url
			return self.getStatus(req)	
		else:
			req.clear()
			req.set_status(412)
			req.finish("Unknown function call")

	''' Grap the tornado req, and process it for a PUT request'''
	def reqprocessPost(self, req):		
		function = req.get_argument('function', 'missing')
		if function == 'missing':
			req.clear()
			req.set_status(412)
			req.finish("Missing function parameter")
		else:
			req.clear()
			req.set_status(412)
			req.finish("Unknown function call")

#	'''
	# Return current status
	def getStatus1(self, req):
		result = {}


		result['AmountOfMediasInDatabase'] = AmountOfMediasInDatabase

		req.clear()
		
		req.set_status(200)
		req.set_header('Content-Type', 'application/json; charset=utf-8')
		req.finish(json.dumps(result))


	# Main call for function.....
	def scanSection(self, req):
		global AmountOfMediasInDatabase

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


		# Background thread starter
		def getStatus(self, req, thread='', section=-1):


			if thread == 'scanMovieDB':
				Thread.Create(self.scanMovieDb(section))



#Thread.Create(backgroundScanThread, globalize=True, title=title, key=key, sectiontype=sectiontype, paths=paths)




		# Get a list of all files in a Movie Library
		def scanMovieDb(sectionNumber):
			global AmountOfMediasInDatabase
			try:
				mediasFromDB = []
				Log.Debug('Starting scanMovieDb for section %s' %(sectionNumber))
#				# Start by getting the totals of this section			
				totalSize = XML.ElementFromURL(self.CoreUrl + sectionNumber + '/all?X-Plex-Container-Start=1&X-Plex-Container-Size=0').get('totalSize')
				AmountOfMediasInDatabase = totalSize
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
				req.finish("Missing section parameter")
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
			AmountOfMediasInDatabase = len(filesFromDatabase)

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

