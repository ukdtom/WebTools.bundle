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

class findUnmatched(object):
	# Defaults used by the rest of the class
	def __init__(self):
		Log.Debug('******* Starting findUnmatched *******')
		self.MovieChuncks = 20
		self.CoreUrl = 'http://127.0.0.1:32400/library/sections/'

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


	# Main call for function.....
	def scanSection(self, req):

		# Get a list of all files in a Library
		def scanMovieDb(sectionNumber):
			try:

				print 'GED Start scanMovieDb'

				mediasFromDB = []
				Log.Debug('Starting scanMovieDb for section %s' %(sectionNumber))
				# Start by getting the totals of this section			
				totalSize = XML.ElementFromURL(self.CoreUrl + sectionNumber + '/all?X-Plex-Container-Start=1&X-Plex-Container-Size=0').get('totalSize')
				Log.Debug('Total size of medias are %s' %(totalSize))
				print 'GED Size 22', totalSize
				# So let's walk the library
				iCurrent = 1
				iStart = 1
				while True:
					# Grap a chunk from the server
					medias = XML.ElementFromURL(self.CoreUrl + sectionNumber + '/all?X-Plex-Container-Start=' + str(iStart) + '&X-Plex-Container-Size=' + str(self.MovieChuncks))
					# Walk the chunk
										
					for media in medias:
#						iCurrent += 1
						parts = media.xpath('//Part')
					
						for part in parts:
							iCurrent += 1
							filename = urllib.quote(unicodedata.normalize('NFKC', urllib.unquote(part.get('file')).decode('utf8')).encode('utf8'))
							# Remove esc backslash if present and on Windows
							if Platform.OS == "Windows":
								filename = filename.replace(':%5C%5C', ':%5C')
							mediasFromDB.append(filename)
							print 'Ged Her',iCurrent, filename
							Log.Debug('**********************************************************')
					
				#	break

					iStart += self.MovieChuncks
					
					if int(medias.get('size')) == 0:
						print 'GED Abort', medias.get('size')
						break


				print mediasFromDB
				print 'Ged len', len(mediasFromDB)

				return mediasFromDB
			except:
				Log.Debug('Fatal error in scanMovieDb')
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




			print 'GED filesFromDatabase:', filesFromDatabase
			print 'GED number', len(filesFromDatabase)
			Log.Debug('************** GED *****************')
	#		Log.Debug(filesFromDatabase)



		







		except:
			Log.Debug('Fatal error happened in scanSection')
			req.clear()
			req.set_status(500)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish('Fatal error happened in scanSection')
			return req






