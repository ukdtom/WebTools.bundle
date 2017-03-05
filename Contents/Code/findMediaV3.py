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
import time, sys, os
from consts import DEBUGMODE
from misc import misc

# Consts used here
AmountOfMediasInDatabase = 0																																												# Int of amount of medias in a database section
mediasFromDB = []																																																		# Files from the database
mediasFromFileSystem = []																																														# Files from the file system
statusMsg = 'idle'																																																	# Response to getStatus
runningState = 0																																																		# Internal tracker of where we are
bAbort = False																																																			# Flag to set if user wants to cancel
Extras = ['behindthescenes','deleted','featurette','interview','scene','short','trailer']														# Local extras
ExtrasDirs = ['behind the scenes', 'deleted scenes', 'featurettes', 'interviews', 'scenes', 'shorts', 'trailers']		# Directories to be ignored
KEYS = ['IGNORE_HIDDEN', 'IGNORED_DIRS', 'VALID_EXTENSIONS'] 																												# Valid keys for prefs
excludeElements='Actor,Collection,Country,Director,Genre,Label,Mood,Producer,Role,Similar,Writer'
excludeFields='summary,tagline'
SUPPORTEDSECTIONS = ['movie', 'show']

DEFAULTPREFS = {
				'IGNORE_HIDDEN' : True,
				'IGNORED_DIRS' : [".@__thumb",".AppleDouble","lost+found"],
				'VALID_EXTENSIONS' : ['3g2', '3gp', 'asf', 'asx', 'avc', 'avi', 'avs', 'bivx', 'bup', 'divx', 'dv', 'dvr-ms', 'evo', 
														'fli', 'flv', 'm2t', 'm2ts', 'm2v', 'm4v', 'mkv', 'mov', 'mp4', 'mpeg', 'mpg', 'mts', 'nsv', 
														'nuv', 'ogm', 'ogv', 'tp', 'pva', 'qt', 'rm', 'rmvb', 'sdp', 'svq3', 'strm', 'ts', 'ty', 'vdr', 
														'viv', 'vob', 'vp3', 'wmv', 'wpl', 'wtv', 'xsp', 'xvid', 'webm'],
				'IGNORE_EXTRAS' : True
				}


GET = ['SCANSECTION', 'GETSECTIONSLIST', 'GETRESULT', 'GETSTATUS', 'GETSETTINGS']
PUT = ['ABORT', 'RESETSETTINGS']
POST = ['SETSETTINGS']
DELETE = []



class findMediaV3(object):	
	init_already = False							# Make sure init only run once
	bResultPresent = False						# Do we have a result to present

	# Init of the class
	@classmethod
	def init(self):
		global retMsg
		global MediaChuncks
		global CoreUrl
		global init_already
		try:
			# Only init once during the lifetime of this
			if not self.init_already:
				self.init_already = True
				retMsg = ['WebTools']
				self.populatePrefs()
				Log.Debug('******* Starting findMedia *******')
				Log.Debug('********* Prefs are ***********')
				Log.Debug(Dict['findMedia'])				
			self.MediaChuncks = 40
			self.CoreUrl = misc.GetLoopBack() + '/library/sections/'
		except Exception, e:
			Log.Exception('Exception in FM Init was %s' %(str(e)))

	#********** Functions below ******************

	# Set settings
	@classmethod
	def SETSETTINGS(self, req, *args):
		try:
			# Get the Payload
			data = json.loads(req.request.body.decode('utf-8'))
		except Exception, e:
			Log.Exception('Not a valid payload: ' + str(e))
			req.set_status(412)
			req.finish('Not a valid payload?')
		try:
			Log.Debug('setSettings called with a body of: ' + str(data))
			# Walk the settings body, and only accept valid settings
			if 'IGNORE_HIDDEN' in data:
				Dict['findMedia']['IGNORE_HIDDEN'] = data['IGNORE_HIDDEN']
			if 'IGNORED_DIRS' in data:
				Dict['findMedia']['IGNORED_DIRS'] = data['IGNORED_DIRS']
			if 'VALID_EXTENSIONS' in data:
				Dict['findMedia']['VALID_EXTENSIONS'] = data['VALID_EXTENSIONS']
			if 'IGNORE_EXTRAS' in data:
				Dict['findMedia']['IGNORE_EXTRAS'] = data['IGNORE_EXTRAS']		
			Dict.Save()
		except Exception, e:
			Log.Exception('Exception in setSettings: ' + str(e))
			req.clear()
			req.set_status(500)
			req.finish('Fatal error in setSettings was: ' + str(e))
		
	# Main call for class.....
	@classmethod
	def SCANSECTION(self, req, *args):
		global AmountOfMediasInDatabase
		global retMsg
		global bAbort
		retMsg = ['WebTools']
		bAbort = False

		# Scan shows from the database
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
					shows = XML.ElementFromURL(self.CoreUrl + sectionNumber + '/all?X-Plex-Container-Start=' + str(iCShow) + '&X-Plex-Container-Size=' + str(self.MediaChuncks) + '&excludeElements=' + excludeElements + '&excludeFields=' + excludeFields).xpath('//Directory')
					# Grap individual show
					for show in shows:
						statusShow = show.get('title')
						statusMsg = statusShows + statusShow					
						iSeason = 0
						iCSeason = 0
						# Grap seasons
						while True:
							seasons = XML.ElementFromURL(misc.GetLoopBack() + show.get('key') + '?X-Plex-Container-Start=' + str(iCSeason) + '&X-Plex-Container-Size=' + str(self.MediaChuncks) + '&excludeElements=' + excludeElements + '&excludeFields=' + excludeFields).xpath('//Directory')
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
									episodes = XML.ElementFromURL(misc.GetLoopBack() + season.get('key') + '?X-Plex-Container-Start=' + str(iCEpisode) + '&X-Plex-Container-Size=' + str(self.MediaChuncks) + '&excludeElements=' + excludeElements + '&excludeFields=' + excludeFields).xpath('//Part')
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
						if DEBUGMODE:
							Log.Debug(mediasFromDB)
						runningState = 1
						break
				return
			except ValueError:
				statusMsg = 'Idle'
				runningState = 99
				Log.Info('Aborted in ScanShowDB')
			except Exception, e:
				Log.Exception('Fatal error in scanShowDB: ' + str(e))
				runningState = 99
		# End scanShowDB

		# Find missing files from the database
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

		# Find missing files from the filesystem
		def findMissingFromFS():
			global MissingFromFS
			Log.Debug('Finding items missing from FileSystem')
			MissingFromFS = []
			try:
				for item in mediasFromDB:
					if bAbort:
						raise ValueError('Aborted')
					if item not in mediasFromFileSystem:
						MissingFromFS.append(item)				
				return MissingFromFS
			except ValueError:
				Log.Info('Aborted in findMissingFromFS')

		# Scan the file system
		def getFiles(filePath):
			global mediasFromFileSystem
			global runningState
			global statusMsg
			try:
				runningState = -1
				Log.Debug("*********************** FileSystem scan Paths: *****************************************")
				bScanStatusCount = 0
				#for filePath in files:
				for Path in filePath:
					# Decode filePath 
					bScanStatusCount += 1
					filePath2 = urllib.unquote(Path).decode('utf8')
					filePath2 = misc.Unicodize(filePath2)					
					Log.Debug("Handling filepath #%s: %s" %(bScanStatusCount, filePath2.encode('utf8', 'ignore')))
					try:
						for root, subdirs, files in os.walk(filePath2):
							if DEBUGMODE:
								Log.Debug('Extreme root: ' + root)
								Log.Debug('Extreme subdirs: ' + str(subdirs))
								Log.Debug('Extreme files: ' + str(files))
							# Need to check if directory in ignore list?
							if os.path.basename(root) in Dict['findMedia']['IGNORED_DIRS']:
								if DEBUGMODE:
									Log.Debug('root in ignored dirs: ' + root)
								continue
							# Lets look at the file
							for file in files:					
								file = misc.Unicodize(file).encode('utf8')
								if DEBUGMODE:
									Log.Debug('file in files: ' + file)
								if bAbort:
									Log.Info('Aborted in getFiles')
									raise ValueError('Aborted')
								if DEBUGMODE:
									Log.Debug('File extention is : ' + os.path.splitext(file)[1][1:].lower())
								if os.path.splitext(file)[1][1:].lower() in Dict['findMedia']['VALID_EXTENSIONS']:
									if DEBUGMODE:
										Log.Debug('File has valid extention, so checking it out')
									# File has a valid extention
									if file.startswith('.') and Dict['findMedia']['IGNORE_HIDDEN']:
										if DEBUGMODE:
											Log.Debug('File hidden, so ignore : ' + file)
										continue
									# Filter out local extras
									if not Dict['findMedia']['IGNORE_EXTRAS']:
										if '-' in file:
											if os.path.splitext(os.path.basename(file))[0].rsplit('-', 1)[1].lower() in Extras:
												if DEBUGMODE:
													Log.Debug('Ignoring Extras file %s' %(os.path.basename(file)))
												continue
										# filter out local extras directories
										if os.path.basename(os.path.normpath(root)).lower() in ExtrasDirs:
											if DEBUGMODE:
												Log.Debug('Ignoring Extras dir %s' %(root))
											continue															
									composed_file = misc.Unicodize(Core.storage.join_path(root,file))						
									if Platform.OS == 'Windows':																		
										# I hate windows
										pos = composed_file.find(':') -1
										if pos != -2:
											# We dont got an UNC path here
											composed_file = composed_file[pos:]								
									mediasFromFileSystem.append(composed_file)
									if DEBUGMODE:
										Log.Debug('Scanning file: ' + file)
										Log.Debug('appending file: ' + composed_file)
									statusMsg = 'Scanning file: ' + file
					except Exception, e:
						Log.Exception('Exception happened in FM scanning filesystem: ' + str(e))
					Log.Debug('***** Finished scanning filesystem *****')
					if DEBUGMODE:
						Log.Debug(mediasFromFileSystem)
					runningState = 2
			except ValueError:
				statusMsg = 'Idle'
				runningState = 99
				Log.Info('Aborted in getFiles')
			except Exception, e:
				Log.Exception('Exception happend in getFiles: ' + str(e))
				runningState = 99

		# Get a list of all files in a Movie Library from the database
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
					medias = XML.ElementFromURL(self.CoreUrl + sectionNumber + '/all?X-Plex-Container-Start=' + str(iStart) + '&X-Plex-Container-Size=' + str(self.MediaChuncks) + '&excludeElements=' + excludeElements + '&excludeFields=' + excludeFields).xpath('//Part')
					# Walk the chunk
					for part in medias:
						if bAbort:
							raise ValueError('Aborted')
						iCount += 1
						filename = part.get('file')		
						filename = unicode(misc.Unicodize(part.get('file')).encode('utf8', 'ignore'))
						mediasFromDB.append(filename)
						statusMsg = 'Scanning database: item %s of %s : Working' %(iCount, totalSize)
					iStart += self.MediaChuncks
					if len(medias) == 0:
						statusMsg = 'Scanning database: %s : Done' %(totalSize)
						Log.Debug('***** Done scanning the database *****')
						if DEBUGMODE:
							Log.Debug(mediasFromDB)
						runningState = 1
						break
				return
			except Exception, e:
				Log.Exception('Fatal error in scanMovieDb: ' + str(e))
				runningState = 99
		# End scanMovieDb


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
				Log.Exception('Exception happend in scanMedias: ' + str(e))
				statusMsg = 'Idle'
	
		# ************ Main function ************ 
		Log.Debug('scanSection started')
		try:
			del mediasFromDB[:]										# Files from the database
			del mediasFromFileSystem[:]						# Files from the file system
			# Grap the section number from the req
			try:
				sectionNumber = args[0][0]
			except:
				Log.Critical('Missing section key')
				req.clear()
				req.set_status(412)
				req.finish('Missing section parameter')

			print 'Ged args', args[0], 'Number: ', sectionNumber

			# Let's find out the info of section here			
			response = XML.ElementFromURL(self.CoreUrl).xpath('//Directory[@key=' + sectionNumber + ']')
			sectionTitle = response[0].get('title')
			sectionType = response[0].get('type')
			locations = response[0].xpath('//Directory[@key=' + sectionNumber + ']/Location')
			sectionLocations = []
			for location in locations:
				sectionLocations.append(os.path.normpath(location.get('path')))
			Log.Debug('Going to scan section %s with a title of %s and a type of %s and locations as %s' %(sectionNumber, sectionTitle, sectionType, str(sectionLocations)))
			if runningState in [0,99]:
				Thread.Create(scanMedias, globalize=True, sectionNumber=sectionNumber, sectionLocations=sectionLocations, sectionType=sectionType, req=req)
			else:
				req.clear()		
				req.set_status(409)
				req.finish('Scanning already in progress')				
		except Exception, ex:
			Log.Exception('Fatal error happened in scanSection: ' + str(ex))
			req.clear()
			req.set_status(500)
			req.finish('Fatal error happened in scanSection: ' + str(ex))
			return req

	# Abort
	@classmethod
	def ABORT(self, req, *args):
		global bAbort
		bAbort = True
		req.clear()		
		req.set_status(200)

	# Get supported Section list
	@classmethod
	def GETSECTIONSLIST(self, req, *args):
		Log.Debug('getSectionsList requested')
		try:
			rawSections = XML.ElementFromURL(misc.GetLoopBack() + '/library/sections')
			Sections=[]
			for directory in rawSections:
				if directory.get('type') in SUPPORTEDSECTIONS:
					Section = {'key':directory.get('key'),'title':directory.get('title'),'type':directory.get('type')}
					Sections.append(Section)		
			req.clear()
			req.set_status(200)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish(json.dumps(Sections))
		except Exception, e:
			Log.Exception('Fatal error happened in getSectionsList: %s' %(str(e)))
			req.clear()
			req.set_status(500)
			req.finish('Fatal error happened in getSectionsList')

	# Return the result
	@classmethod
	def GETRESULT(self, req, *args):
		# Are we in idle mode?
		if runningState == 0:
			req.clear()		
			if 'WebTools' in retMsg:
				req.set_status(204)
			else:
				Log.Info('Result is: ' + str(retMsg))
				req.set_status(200)
				req.set_header('Content-Type', 'application/json; charset=utf-8')
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
	@classmethod
	def GETSTATUS(self, req, *args):
		global runningState		
		req.clear()		
		req.set_status(200)
		if runningState == 0:
			req.finish('Idle')	
		else:
			req.finish(statusMsg)

	# Reset settings to default
	@classmethod
	def RESETSETTINGS(self, req, *args):
		Dict['findMedia'] = None
		self.populatePrefs()
		req.clear()		
		req.set_status(200)

	# Return the settings of this plugin
	@classmethod
	def GETSETTINGS(self, req, *args):
		req.clear()		
		req.set_header('Content-Type', 'application/json; charset=utf-8')
		req.set_status(200)
		req.finish(json.dumps(Dict['findMedia']))

	''' Get the relevant function and call it with optinal params '''
	@classmethod
	def getFunction(self, metode, req, *args):		
		self.init()
		params = req.request.uri[8:].upper().split('/')		
		self.function = None
		if metode == 'get':
			for param in params:
				if param in GET:
					self.function = param
					break
				else:
					pass
		elif metode == 'post':
			for param in params:
				if param in POST:
					self.function = param
					break
				else:
					pass
		elif metode == 'put':
			for param in params:
				if param in PUT:
					self.function = param
					break
				else:
					pass
		elif metode == 'delete':
			for param in params:
				if param in DELETE:
					self.function = param
					break
				else:
					pass
		if self.function == None:
			Log.Debug('Function to call is None')
			req.clear()
			req.set_status(404)
			req.finish('Unknown function call')
		else:		
			# Check for optional argument
			paramsStr = req.request.uri[req.request.uri.upper().find(self.function) + len(self.function):]			
			# remove starting and ending slash
			if paramsStr.endswith('/'):
				paramsStr = paramsStr[:-1]
			if paramsStr.startswith('/'):
				paramsStr = paramsStr[1:]
			# Turn into a list
			params = paramsStr.split('/')
			# If empty list, turn into None
			if params[0] == '':
				params = None
			try:
				Log.Debug('Function to call is: ' + self.function + ' with params: ' + str(params))
				if params == None:
					getattr(self, self.function)(req)
				else:
					getattr(self, self.function)(req, params)
			except Exception, e:
				Log.Exception('Exception in process of: ' + str(e))

################### Internal functions #############################

	''' Populate the defaults, if not already there '''
	@classmethod
	def populatePrefs(self):
		if Dict['findMedia'] == None:
			Dict['findMedia'] = DEFAULTPREFS
			Dict.Save()
		# New key from V3.0, so need to handle seperately
		if 'IGNORE_EXTRAS' not in Dict['findMedia'].keys():
			Dict['findMedia']['IGNORE_EXTRAS'] = True
			Dict.Save()




