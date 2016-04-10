######################################################################################################################
#	findMedia unit				
# A WebTools bundle plugin	
#
# Used to locate both items missing from the database, as well as from the filesystem
#
#	Author: dane22, a Plex Community member
#
######################################################################################################################

import urllib
import unicodedata
import json
import time

# Consts used here
AmountOfMediasInDatabase = 0																																				# Int of amount of medias in a database section
mediasFromDB = []																																										# Files from the database
mediasFromFileSystem = []																																						# Files from the file system
statusMsg = 'idle'																																									# Response to getStatus
runningState = 0																																										# Internal tracker of where we are
bAbort = False																																											# Flag to set if user wants to cancel
Extras = ['behindthescenes','deleted','featurette','interview','scene','short','trailer']						# Local extras
KEYS = ['IGNORE_HIDDEN', 'IGNORED_DIRS', 'VALID_EXTENSIONS'] 																				# Valid keys for prefs


class findMedia(object):	
	init_already = False							# Make sure init only run once
	bResultPresent = False						# Do we have a result to present

	# Defaults used by the rest of the class
	def __init__(self):
		global retMsg
		# Only init once during the lifetime of this
		if not findMedia.init_already:
			findMedia.init_already = True
			retMsg = ['WebTools']
			self.populatePrefs()
			Log.Debug('******* Starting findMedia *******')
		self.MediaChuncks = 40
		self.CoreUrl = 'http://127.0.0.1:32400/library/sections/'

	''' Populate the defaults, if not already there '''
	def populatePrefs(self):
		if Dict['findMedia'] == None:
			Dict['findMedia'] = {
				'IGNORE_HIDDEN' : True,
				'IGNORED_DIRS' : [".@__thumb",".AppleDouble","lost+found"],
				'VALID_EXTENSIONS' : ['.m4v', '.3gp', '.nsv', '.ts', '.ty', '.strm', '.rm', '.rmvb', '.m3u',
															'.mov', '.qt', '.divx', '.xvid', '.bivx', '.vob', '.nrg', '.img', '.iso', 
															'.pva', '.wmv', '.asf', '.asx', '.ogm', '.m2v', '.avi', '.bin', '.dat', 
															'.dvr-ms', '.mpg', '.mpeg', '.mp4', '.mkv', '.avc', '.vp3', '.svq3', '.nuv',
															'.viv', '.dv', '.fli', '.flv', '.rar', '.001', '.wpl', '.zip', '.mp3']				
				}
			Dict.Save()

	''' Grap the tornado req, and process it '''
	def reqprocess(self, req):	
		function = req.get_argument('function', 'missing')
		if function == 'missing':
			req.clear()
			req.set_status(412)
			req.finish("Missing function parameter")
		elif function == 'scanSection':
			# Call scanSection
			return self.scanSection(req)
		elif function == 'getStatus':
			# Call scanSection
			return self.getStatus(req)	
		elif function == 'getResult':
			# Call getResult
			return self.getResult(req)
		elif function == 'getSettings':
			# Call getSettings
			return self.getSettings(req)
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
		elif function == 'resetSettings':
			# Call resetSettings
			return self.resetSettings(req)
		elif function == 'setSetting':
			# Call resetSetting
			return self.setSetting(req)
		elif function == 'abort':
			# Call abort
			return self.abort(req)
		else:
			req.clear()
			req.set_status(412)
			req.finish("Unknown function call")

	# Abort
	def abort(self, req):
		global bAbort
		abort = req.get_argument('abort', 'missing')
		if abort == 'missing':
			req.clear()
			req.set_status(412)
			req.finish("Missing abort parameter")
		if abort == 'true':
			bAbort = True
			req.clear()		
			req.set_status(200)


	# Set settings
	def setSetting(self, req):
		try:
			key = req.get_argument('key', 'missing')
			if key == 'missing':
				req.clear()
				req.set_status(412)
				req.finish("Missing key parameter")
			if key not in KEYS:
				req.clear()
				req.set_status(412)
				req.finish("Unknown key parameter")




			value = req.get_argument('value', 'missing')
			if value == 'missing':
				req.clear()
				req.set_status(412)
				req.finish("Missing value parameter")

			print 'Ged2', value
			value = value.replace("u'", "")
			value = value.split(',')

			for item in value:
				print 'Ged3', item


			print 'Ged4', value

#str.replace(old, new[, max])

			Dict['findMedia'][key] = value
			Dict.Save()
			req.clear()		
			req.set_status(200)
		except Exception, e:
			Log.Debug('Fatal error in setSetting: ' + str(e))
			req.clear()
			req.set_status(500)
			req.finish("Unknown error happened in findMedia-setSetting: " + str(e))


	# Reset settings to default
	def resetSettings(self, req):
		Dict['findMedia'] = None
		self.populatePrefs()
		req.clear()		
		req.set_header('Content-Type', 'application/json; charset=utf-8')
		req.set_status(200)

	# Return the settings of this plugin
	def getSettings(self, req):
		req.clear()		
		req.set_header('Content-Type', 'application/json; charset=utf-8')
		req.set_status(200)
		req.finish(json.dumps(Dict['findMedia']))

	# Return the result
	def getResult(self, req):
		# Are we in idle mode?
		if runningState == 0:
			req.clear()		
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			if 'WebTools' in retMsg:
				req.set_status(204)
			else:
				req.set_status(200)
				req.finish(retMsg)
		elif runningState == 99: 
			if bAbort:
				req.set_status(204)
			else:
				req.set_status(204)
		else:
			req.clear()
			req.set_status(204)
		return

	# Return current status
	def getStatus(self, req):
		global runningState		
		req.clear()		
		req.set_status(200)
		req.set_header('Content-Type', 'application/json; charset=utf-8')
		if runningState == 0:
			req.finish('Idle')	
		else:
			req.finish(statusMsg)

	# Main call for function.....
	def scanSection(self, req):
		global AmountOfMediasInDatabase
		global retMsg
		global bAbort
		retMsg = ['WebTools']
		bAbort = False
	
		def findMissingFromFS():
			global MissingFromFS
			Log.Debug('Finding items missing from FileSystem')
			MissingFromFS = []
			try:
				for item in mediasFromDB:
					if bAbort:
						raise ValueError('Aborted')
					if not os.path.isfile(item):
						MissingFromFS.append(item)
				return MissingFromFS
			except ValueError:
				Log.Info('Aborted in findMissingFromFS')

		def findMissingFromDB():
			global MissingFromDB
			Log.Debug('Finding items missing from Database')
			MissingFromDB = []
			try:
				for item in mediasFromFileSystem:
					if bAbort:
						raise ValueError('Aborted')
					if item not in mediasFromDB:
						MissingFromDB.append(item)
				return MissingFromDB
			except ValueError:
				Log.Info('Aborted in findMissingFromDB')

		# Scan db and files. Must run as a thread
		def scanMedias(sectionNumber, sectionLocations, sectionType, req):
			global runningState
			global statusMsg
			global retMsg
			try:
				if sectionType == 'movie':
					scanMovieDb(sectionNumber=sectionNumber)
				elif sectionType == 'show':
					scanShowDB(sectionNumber=sectionNumber)
				else:
					req.clear()
					req.set_status(400)
					req.finish('Unknown Section Type')			
				if bAbort:
					raise ValueError('Aborted')
				getFiles(sectionLocations)
				if bAbort:
					raise ValueError('Aborted')
				retMsg = {}
				statusMsg = 'Get missing from File System'
				retMsg["MissingFromFS"] = findMissingFromFS()
				if bAbort:
					raise ValueError('Aborted')
				statusMsg = 'Get missing from database'
				retMsg["MissingFromDB"] = findMissingFromDB()	
				runningState = 0
				statusMsg = 'done'
			except ValueError:
				Log.Info('Aborted in ScanMedias')
			except Exception, e:
				Log.Critical('Exception happend in scanMedias: ' + str(e))
				statusMsg = 'Idle'

		# Scan the file system
		def getFiles(filePath):
			global mediasFromFileSystem
			global runningState
			global statusMsg
			try:
				runningState = -1
				Log.Debug("*********************** FileSystem Paths: *****************************************")
				bScanStatusCount = 0
				files = str(filePath)[2:-2].replace("'", "").split(', ')
				Log.Debug(files)
				for filePath in files:
					# Decode filePath 
					bScanStatusCount += 1
					filePath2 = urllib.unquote(filePath).decode('utf8')
					if filePath2.startswith('u'):
						filePath2 = filePath2[1:]
					Log.Debug("Handling file #%s: %s" %(bScanStatusCount, String.Unquote(filePath2).encode('utf8', 'ignore')))
					for root, subdirs, files in os.walk(String.Unquote(filePath2).encode('utf8', 'ignore')):
						# Need to check if directory in ignore list?
						if os.path.basename(root) in Dict['findMedia']['IGNORED_DIRS']:
							continue
						# Lets look at the file
						for file in files:
							if bAbort:
								Log.Info('Aborted in getFiles')
								raise ValueError('Aborted')
							if os.path.splitext(file)[1] in Dict['findMedia']['VALID_EXTENSIONS']:
								# File has a valid extention
								if file.startswith('.') and Dict['findMedia']['IGNORE_HIDDEN']:
									continue
								# Filter out local extras
								if '-' in file:
									if os.path.splitext(os.path.basename(file))[0].rsplit('-', 1)[1] in Extras:
										continue
								mediasFromFileSystem.append(Core.storage.join_path(root,file))
								statusMsg = 'Scanning file: ' + file
					Log.Debug('***** Finished scanning filesystem *****')
#					Log.Debug(mediasFromFileSystem)
					runningState = 2
			except ValueError:
				statusMsg = 'Idle'
				runningState = 99
				Log.Info('Aborted in getFiles')
			except Exception, e:
				Log.Critical('Exception happend in getFiles: ' + str(e))
				runningState = 99

		def scanShowDB(sectionNumber=0):
			global AmountOfMediasInDatabase
			global mediasFromDB
			global statusMsg
			global runningState
			try:				
				Log.Debug('Starting scanShowDB for section %s' %(sectionNumber))
				runningState = -1
				statusMsg = 'Starting to scan database for section %s' %(sectionNumber)
				# Start by getting the totals of this section			
				totalSize = XML.ElementFromURL(self.CoreUrl + sectionNumber + '/all?X-Plex-Container-Start=1&X-Plex-Container-Size=0').get('totalSize')
				AmountOfMediasInDatabase = totalSize
				Log.Debug('Total size of medias are %s' %(totalSize))
				iShow = 0
				iCShow = 0
				statusShows = 'Scanning database show %s of %s : ' %(iShow, totalSize)
				statusMsg = statusShows
				# So let's walk the library
				while True:
					# Grap shows
					shows = XML.ElementFromURL(self.CoreUrl + sectionNumber + '/all?X-Plex-Container-Start=' + str(iCShow) + '&X-Plex-Container-Size=' + str(self.MediaChuncks)).xpath('//Directory')
					# Grap individual show
					for show in shows:
						statusShow = show.get('title')
						statusMsg = statusShows + statusShow					
						iSeason = 0
						iCSeason = 0
						# Grap seasons
						while True:
							seasons = XML.ElementFromURL('http://127.0.0.1:32400' + show.get('key') + '?X-Plex-Container-Start=' + str(iCSeason) + '&X-Plex-Container-Size=' + str(self.MediaChuncks)).xpath('//Directory')
							# Grap individual season
							for season in seasons:			
								if season.get('title') == 'All episodes':
									iSeason += 1
									continue
								statusSeason = ' ' + season.get('title')							
								statusMsg = statusShows + statusShow + statusSeason
								iSeason += 1
								# Grap Episodes
								iEpisode = 0
								iCEpisode = 0
								while True:
									episodes = XML.ElementFromURL('http://127.0.0.1:32400' + season.get('key') + '?X-Plex-Container-Start=' + str(iCEpisode) + '&X-Plex-Container-Size=' + str(self.MediaChuncks)).xpath('//Part')
									for episode in episodes:
										if bAbort:
											raise ValueError('Aborted')
										filename = episode.get('file')		
										filename = String.Unquote(filename).encode('utf8', 'ignore')	
										mediasFromDB.append(filename)
										iEpisode += 1
									# Inc Episodes counter
									iCEpisode += self.MediaChuncks
									if len(episodes) == 0:
										break
							# Inc Season counter
							iCSeason += self.MediaChuncks
							if len(seasons) == 0:
								break
						iShow += 1
						statusShows = 'Scanning database show %s of %s : ' %(iShow, totalSize)					
					# Inc. Shows counter
					iCShow += self.MediaChuncks					
					if len(shows) == 0:
						statusMsg = 'Scanning database: %s : Done' %(totalSize)
						Log.Debug('***** Done scanning the database *****')
#						Log.Debug(mediasFromDB)
						runningState = 1
						break
				return
			except ValueError:
				statusMsg = 'Idle'
				runningState = 99
				Log.Info('Aborted in ScanShowDB')
			except Exception, e:
				Log.Debug('Fatal error in scanShowDB: ' + str(e))
				runningState = 99
		# End scanShowDB

		# Get a list of all files in a Movie Library
		def scanMovieDb(sectionNumber=0):
			global AmountOfMediasInDatabase
			global mediasFromDB
			global statusMsg
			global runningState
			try:				
				Log.Debug('Starting scanMovieDb for section %s' %(sectionNumber))
				runningState = -1
				statusMsg = 'Starting to scan database for section %s' %(sectionNumber)
				# Start by getting the totals of this section			
				totalSize = XML.ElementFromURL(self.CoreUrl + sectionNumber + '/all?X-Plex-Container-Start=1&X-Plex-Container-Size=0').get('totalSize')
				AmountOfMediasInDatabase = totalSize
				Log.Debug('Total size of medias are %s' %(totalSize))
				iStart = 0
				iCount = 0
				statusMsg = 'Scanning database item %s of %s : Working' %(iCount, totalSize)
				# So let's walk the library
				while True:
					# Grap a chunk from the server
					medias = XML.ElementFromURL(self.CoreUrl + sectionNumber + '/all?X-Plex-Container-Start=' + str(iStart) + '&X-Plex-Container-Size=' + str(self.MediaChuncks)).xpath('//Part')
					# Walk the chunk
					for part in medias:
						if bAbort:
							raise ValueError('Aborted')
						iCount += 1
						filename = part.get('file')		
						filename = String.Unquote(filename).encode('utf8', 'ignore')	
						mediasFromDB.append(filename)
						statusMsg = 'Scanning database: item %s of %s : Working' %(iCount, totalSize)
					iStart += self.MediaChuncks
					if len(medias) == 0:
						statusMsg = 'Scanning database: %s : Done' %(totalSize)
						Log.Debug('***** Done scanning the database *****')
#						Log.Debug(mediasFromDB)
						runningState = 1
						break
				return
			except Exception, e:
				Log.Debug('Fatal error in scanMovieDb: ' + str(e))
				runningState = 99
		# End scanMovieDb

# ************ Main function ************ 
		Log.Debug('scanSection started')
		try:
			del mediasFromDB[:]										# Files from the database
			del mediasFromFileSystem[:]						# Files from the file system
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
			if runningState in [0,99]:
				Thread.Create(scanMedias, globalize=True, sectionNumber=sectionNumber, sectionLocations=sectionLocations, sectionType=sectionType, req=req)
			else:
				req.clear()		
				req.set_status(409)
				req.set_header('Content-Type', 'application/json; charset=utf-8')
				req.finish('Scanning already in progress')				
		except Exception, ex:
			Log.Debug('Fatal error happened in scanSection: ' + str(ex))
			req.clear()
			req.set_status(500)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish('Fatal error happened in scanSection: ' + str(ex))
			return req

