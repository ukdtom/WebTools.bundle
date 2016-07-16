######################################################################################################################
#	NFO Exporter module for WebTools
#
#	Author: dane22, a Plex Community member
#
######################################################################################################################

import os, io
import mmap
from consts import DEBUGMODE
import datetime
from lxml import etree
from shutil import move

statusMsg = 'idle'																																									# Response to getStatus
runningState = 0																																										# Internal tracker of where we are
bAbort = False																																											# Flag to set if user wants to cancel

class nfoExporter(object):
	init_already = False							# Make sure init only run once
	bResultPresent = False						# Do we have a result to present

	# Defaults used by the rest of the class
	def __init__(self):
		self.MediaChuncks = 40
		self.CoreUrl = 'http://127.0.0.1:32400/library/sections/'
		# Only init once during the lifetime of this
		if not nfoExporter.init_already:
			nfoExporter.init_already = True
			self.populatePrefs()

			Log.Debug('******* Starting nfoExporter *******')



	''' Populate the defaults, if not already there '''
	def populatePrefs(self):
		if Dict['nfoExportTimeStamps'] == None:
			Dict['nfoExportTimeStamps'] = {}
			Dict.Save()


	''' Grap the tornado req, and process it for a POST request'''
	def reqprocessPost(self, req):
		function = req.get_argument('function', 'missing')
		if function == 'missing':
			req.clear()
			req.set_status(412)
			req.finish("<html><body>Missing function parameter</body></html>")
		elif function == 'export':
			return self.export(req)
		else:
			req.clear()
			req.set_status(412)
			req.finish("<html><body>Unknown function call</body></html>")

	# Make a backup, if nfo file isn't from WebTools
	def makeNFOBackup(self, fileName):
		if os.path.isfile(fileName):
			Log.Debug('Found existing nfo file')
			try:
				# Our nfo file or belonging to somebody else?
				with io.open(fileName) as f:
					s = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
					if s.find('Made by WebTools') == -1:
						# We need to rename the file, to prevent we erase peoples stuff
						path, nfoFileName = os.path.split(fileName)
						bakFile = Core.storage.join_path(path, 'WT-ORIGINAL-' + nfoFileName)
						Log.Debug('Renaming file: ' + fileName + ' to WT-ORIGINAL-' + nfoFileName)	
						os.rename(fileName, bakFile)
			except Exception, e:
				pass
		else:
			Log.Debug('Existing .nfo file not found')



	def export(self, req):

		''' Return the type of the section '''
		def getSectionType(section):
			url = 'http://127.0.0.1:32400/library/sections/' + section + '/all?X-Plex-Container-Start=1&X-Plex-Container-Size=0'
			return XML.ElementFromURL(url).xpath('//MediaContainer/@viewGroup')[0]

		def scanMovieSection(req, sectionNumber):
			Log.Debug('Starting scanMovieSection')		
			global AmountOfMediasInDatabase
			global mediasFromDB
			global statusMsg
			global runningState
			try:		
				# Start by getting the last timestamp for a scanning:
				if sectionNumber in Dict['nfoExportTimeStamps'].keys():					
					timeStamp = Dict['nfoExportTimeStamps'][sectionNumber]
				else:
					# Setting key for section to epoch start
					Dict['nfoExportTimeStamps'][sectionNumber] = 0
					Dict.Save()
					timeStamp = 0


				print 'Ged FAKE Timestamp REMOVE'
#				timeStamp = 1468544934
#				timeStamp = 0
				now = int((datetime.datetime.now()-datetime.datetime(1970,1,1)).total_seconds())	
				Log.Debug('Starting scanMovieDb for section %s' %(sectionNumber))
				Log.Debug('Only grap medias updated since: ' + datetime.datetime.fromtimestamp(int(timeStamp)).strftime('%Y-%m-%d %H:%M:%S'))
				runningState = -1
				statusMsg = 'Starting to scan database for section %s' %(sectionNumber)
				# Start by getting the totals of this section			
				totalSize = XML.ElementFromURL(self.CoreUrl + sectionNumber + '/all?updatedAt>=' + str(timeStamp) + '&X-Plex-Container-Start=1&X-Plex-Container-Size=0').get('totalSize')
				AmountOfMediasInDatabase = totalSize
				Log.Debug('Total size of medias are %s' %(totalSize))

				if totalSize == '0':					
					# Stamp dict with new timestamp
					Dict['nfoExportTimeStamps'][sectionNumber] = now
					Dict.Save()
					Log.Debug('Nothing to process...Exiting')
					return
				iStart = 0
				iCount = 0
				statusMsg = 'Scanning database item %s of %s : Working' %(iCount, totalSize)
				# So let's walk the library
				while True:
					# Grap a chunk from the server
					videos = XML.ElementFromURL(self.CoreUrl + sectionNumber + '/all?updatedAt>=' + str(timeStamp) + '&X-Plex-Container-Start=' + str(iStart) + '&X-Plex-Container-Size=' + str(self.MediaChuncks)).xpath('//Video')
					# Walk the chunk

					for video in videos:
						if bAbort:
							raise ValueError('Aborted')
						iCount += 1
						videoDetails = XML.ElementFromURL('http://127.0.0.1:32400/library/metadata/' + video.get('ratingKey')).xpath('//Video')[0]

						try:
							''' Create an XML Element tree for the .nfo file '''					
							# Namespace and xsd
							ns1 = 'http://www.w3.org/2001/XMLSchema-instance'
							ns2 = 'http://www.w3.org/2001/XMLSchema'
							location_attribute = '{%s}xsd' % ns1
							# Create the root element
							nfo = etree.Element('movie')
							nfo.set(location_attribute, ns2)
							# Comment below is mandentory, since we use that to track, if the .nfo file is ours
							nfo.addprevious(etree.Comment('Made by WebTools'))
							# Make a new document tree
							doc = etree.ElementTree(nfo)

							''' Now digest the media, and add to the XML '''
							# Id
							try:
								guid = videoDetails.get('guid').split('//')[1].split('?')[0]
								Id = etree.SubElement(nfo, 'id')
								if 'imdb' in videoDetails.get('guid'):
									Id.text = unicode(guid)
								if 'themoviedb' in videoDetails.get('guid'):
									Id.set('TMDB', guid)
							except:
								pass
							# Title
							try:
								title = etree.SubElement(nfo, 'title')
								title.text = unicode(videoDetails.get('title'))
							except:
								pass
							# originalTitle
							try:
								originaltitle = etree.SubElement(nfo, 'originaltitle')
								originaltitle.text = unicode(videoDetails.get('originalTitle'))
							except:
								pass
							# titleSort
							try:
								titlesort = etree.SubElement(nfo, 'titlesort')
								titlesort.text = unicode(videoDetails.get('titleSort'))
							except:
								pass
							# Summery aka plot
							try:
								summary = etree.SubElement(nfo, 'plot')
								summary.text = unicode(videoDetails.get('summary'))
							except:
								pass
							# rating
							try:
								rating = etree.SubElement(nfo, 'rating')
								rating.text = unicode(videoDetails.get('rating'))
							except:
								pass
							# ratingsource
							try:
								ratingsource = etree.SubElement(nfo, 'ratingsource')
								ratingsource.text = unicode(videoDetails.get('ratingImage').split(':')[0])
							except:
								pass
							# contentRating
							try:
								contentRating = etree.SubElement(nfo, 'contentRating')
								contentRating.text = unicode(videoDetails.get('contentRating'))
							except:
								pass
							# studio
							try:
								studio = etree.SubElement(nfo, 'studio')
								studio.text = unicode(videoDetails.get('studio'))
							except:
								pass
							# year
							try:
								year = etree.SubElement(nfo, 'year')
								year.text = unicode(videoDetails.get('year'))
							except:
								pass
							# tagline
							try:
								tagline = etree.SubElement(nfo, 'tagline')
								tagline.text = unicode(videoDetails.get('tagline'))
							except:
								pass
							# Genre
							try:
								Genres = videoDetails.xpath('//Genre')
								for Genre in Genres:
									try:
										genre = etree.SubElement(nfo, 'genre')
										genre.text = unicode(Genre.xpath('@tag')[0])
									except:
										pass
							except:
								pass
							# Collection
							try:
								Collections = videoDetails.xpath('//Collection')
								for Collection in Collections:
									try:
										collection = etree.SubElement(nfo, 'collection')
										collection.text = unicode(Collection.xpath('@tag')[0])
									except:
										pass
							except:
								pass
							# originallyAvailableAt aka releasedate
							try:
								releasedate = etree.SubElement(nfo, 'releasedate')
								releasedate.text = unicode(videoDetails.get('originallyAvailableAt'))
							except:
								pass
							# Director
							try:
								Directors = videoDetails.xpath('//Director')
								for Director in Directors:
									try:
										director = etree.SubElement(nfo, 'director')
										director.text = unicode(Director.xpath('@tag')[0])
									except:
										pass
							except:
								pass
							# Writer
							try:
								Writers = videoDetails.xpath('//Writer')
								for Writer in Writers:
									try:
										writer = etree.SubElement(nfo, 'writer')
										writer.text = unicode(Writer.xpath('@tag')[0])
									except:
										pass
							except:
								pass
							# Producer
							try:
								Producers = videoDetails.xpath('//Producer')
								for Producer in Producers:
									try:
										producer = etree.SubElement(nfo, 'producer')
										producer.text = unicode(Producer.xpath('@tag')[0])
									except:
										pass
							except:
								pass
							# Country
							try:
								Countries = videoDetails.xpath('//Country')
								for Country in Countries:
									try:
										country = etree.SubElement(nfo, 'country')
										country.text = unicode(Country.xpath('@tag')[0])
									except:
										pass
							except:
								pass
							# Role aka actor
							try:
								Roles = videoDetails.xpath('//Role')
								orderNo = 1
								for Role in Roles:
									role = etree.SubElement(nfo, 'actor')
									# name
									try:
										name = etree.SubElement(role, 'name')
										name.text = unicode(Role.xpath('@tag')[0])
									except:
										pass
									# role
									try:
										actorRole = etree.SubElement(role, 'role')
										actorRole.text = unicode(Role.xpath('@role')[0])
									except:
										pass
									# order
									try:
										order = etree.SubElement(role, 'order')
										order.text = unicode(orderNo)
										orderNo += 1
									except:
										pass
									# thumb
									try:
										thumb = etree.SubElement(role, 'thumb')
										thumb.text = Role.xpath('@thumb')[0]
									except:
										pass
							except:
								pass
							# Let's start by grapping relevant files for this movie
							fileNames = videoDetails.xpath('//Part')
							for fileName in fileNames:
								filename = fileName.xpath('@file')[0]
								filename = String.Unquote(filename).encode('utf8', 'ignore')
								# Get name of nfo file
								nfoFile = os.path.splitext(filename)[0] + '.nfo'
								Log.Debug('Name and path to nfo file is: ' + nfoFile)
								self.makeNFOBackup(nfoFile)
								# Now save the .nfo file
								doc.write(nfoFile, xml_declaration=True, pretty_print=True, encoding='UTF-8')

								# Make poster
								posterUrl = 'http://127.0.0.1:32400' + videoDetails.get('thumb')
								targetFile = os.path.splitext(filename)[0] + '-poster.jpg'
								response = HTTP.Request(posterUrl)
								with io.open( targetFile, 'wb' ) as fo:
									fo.write( response.content )
									Log.Debug('Poster saved as %s' %targetFile)
								# Make fanart
								posterUrl = 'http://127.0.0.1:32400' + videoDetails.get('art')
								targetFile = os.path.splitext(filename)[0] + '-fanart.jpg'
								response = HTTP.Request(posterUrl)
								with io.open( targetFile, 'wb' ) as fo:
									fo.write( response.content )
									Log.Debug('FanArt saved as %s' %targetFile)



						except Exception, e:
							Log.Exception('Exception happend in generating nfo file: ' + str(e))			

						statusMsg = 'Scanning database: item %s of %s : Working' %(iCount, totalSize)
					iStart += self.MediaChuncks
					if len(videos) == 0:
						statusMsg = 'Scanning database: %s : Done' %(totalSize)
						Log.Debug('***** Done scanning the database *****')
						runningState = 1
						break
				# Stamp dict with new timestamp
				Dict['nfoExportTimeStamps'][sectionNumber] = now
				Dict.Save()
				return
			except Exception, e:
				Log.Exception('Fatal error in scanMovieDb: ' + str(e))
				runningState = 99
		# End scanMovieDb


		def scanShowSection(req, sectionNumber):
			print 'Ged1 scanShowSection'	


		# ********** Main function **************
		Log.Info('nfo export called')
		try:
			section = req.get_argument('section', '_export_missing_')
			if section == '_export_missing_':
				req.clear()
				req.set_status(412)
				req.finish("<html><body>Missing section parameter</body></html>")
			if getSectionType(section) == 'movie':
				scanMovieSection(req, section)
			elif getSectionType(section) == 'show':
				scanShowSection(req, section)
			else:
				Log.debug('Unknown section type for section:' + section + ' type: ' + getSectionType(section))
				req.clear()
				req.set_status(404)
				req.finish("Unknown sectiontype")
		except Exception, e:
			Log.Exception('Exception in nfo export' + str(e))







