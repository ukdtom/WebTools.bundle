######################################################################################################################
#					WebTools helper unit
#
#					Runs a seperate webserver on a specified port
#
#					Author:			dagaluf, a Plex Community member
#					Author:			dane22, a Plex Community member
#
#					Support thread:	https://forums.plex.tv/index.php/topic/119940-webtool-subtitle-manager-development/
#
######################################################################################################################

from tornado.web import RequestHandler, StaticFileHandler, Application, HTTPError
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.escape import json_encode

import threading
from datetime import date
from random import randint
import json
from xml.etree import ElementTree
from itertools import islice

#************** webTools functions ******************************
''' Here we have the supported functions '''
class webTools(object):
	''' Return version number '''
	def getVersion(self):
		Log.Debug('Version requested')
		return {	'version': Dict['SharedSecret']}

	''' Check if mySecret is correct and in the header '''
	def checkSecret(self, headers):

		#TODO Rem out next line when not coding to disable auth
		return True

		if 'Mysecret' in headers:
			if Hash.MD5(Dict['SharedSecret']) == headers['Mysecret']:
				Log.Debug('mySecret is okay')
				return True
			else:
				Log.Debug('mySecret missing or wrong')
				return False

	''' Return webpart settings '''
	def getSettings(self, params):
		Log.Debug('Settings requested')
		if params['param2'] != None:
			if Dict[params['param2']] == None:
				return 406
			else:
				if params['param2'] == 'items_per_page':
					Log.Debug('Settings returned %s' %(json.dumps(int(Dict[params['param2']]))))
					return json.dumps(int(Dict['items_per_page']))
				else:
					return json.dumps(Dict[params['param2']] == 'true')
		mySetting = {}
		mySetting['options_hide_integrated'] = (Dict['options_hide_integrated'] == 'true')
		mySetting['options_hide_local'] = (Dict['options_hide_local'] == 'true')
		mySetting['options_only_multiple'] = (Dict['options_only_multiple'] == 'true')
		mySetting['items_per_page'] = int(Dict['items_per_page'])
		mySetting['fatal_error'] = (Dict['fatal_error'] == 'true')
		return json.dumps(mySetting)

	''' get Show info '''
	def getShow(self, params):
		Log.Debug('getShow called with parameters: %s' %(params))
		if params['param2'] != None:
			if params['param2'] == 'season':
				Log.Debug('Got a season request')
				myURL = 'http://127.0.0.1:32400/library/metadata/' + params['param3'] + '/tree'
				episodes = XML.ElementFromURL(myURL).xpath('//MetadataItem/MetadataItem')
				mySeason = []
				for episode in episodes:
					myEpisode = {}
					myEpisode['key'] = episode.get('id')					
					myEpisode['title'] = episode.get('title')					
					myEpisode['episode'] = episode.get('index')
					if params['param4'] == 'getsubs':
						# We need to get subtitle info as well here
						if params['param5'] == None:
							subParams = {'param3': None, 'param2': episode.get('id'), 'param1': 'subtitles'}
						if params['param5'] == 'all':
							subParams = {'param3': 'all', 'param2': episode.get('id'), 'param1': 'subtitles'}
						subs = self.getSubTitles(subParams)
						myEpisode['subtitles'] = subs
					mySeason.append(myEpisode)
				return mySeason					
			else:
				if params['param3'] == 'size':
					Log.Debug('Size requested for section %s' %(params['param2']))
					myURL = 'http://127.0.0.1:32400/library/metadata/' + params['param2'] + '/allLeaves?X-Plex-Container-Start=0&X-Plex-Container-Size=1'
					try:
						size = XML.ElementFromURL(myURL).get('totalSize')		
						Log.Debug('Returning size as %s' %(size))				
						return size
					except:					
						return 404
				elif params['param3'] == 'seasons':
					myURL = 'http://127.0.0.1:32400/library/metadata/' + params['param2'] + '/children'				
					mySeasons = []
					seasons = XML.ElementFromURL(myURL).xpath('//Directory')
					if len(seasons) == 1:
						for season in seasons:
							mySeason = {}
							mySeason['key'] = season.get('ratingKey')
							mySeason['season'] = season.get('index')
							mySeason['size'] = season.get('leafCount')					
							mySeasons.append(mySeason)
					else:
						for season in islice(seasons, 1, None):
							mySeason = {}
							mySeason['key'] = season.get('ratingKey')
							mySeason['season'] = season.get('index')
							mySeason['size'] = season.get('leafCount')					
							mySeasons.append(mySeason)
					return mySeasons
				else:
					if params['param4'] != None:
						myURL = 'http://127.0.0.1:32400/library/metadata/' + params['param2'] + '/allLeaves?X-Plex-Container-Start=' + params['param3'] + '&X-Plex-Container-Size=' + params['param4']
						rawEpisodes = XML.ElementFromURL(myURL).xpath('//Video')
						episodes=[]
						for media in rawEpisodes:
							episode = {}
							episode['key'] = media.get('ratingKey')
							episode['title'] = media.get('title')
							episode['season'] = media.get('parentIndex')
							episode['episode'] = media.get('index')
							if params['param5'] == None:
								episodes.append(episode)
							elif params['param5'] == 'getsubs':
								# We need to get subtitle info as well here
								if params['param6'] == None:
									subParams = {'param4': None, 'param3': None, 'param2': media.get('ratingKey'), 'param1': 'subtitles'}
								if params['param6'] == 'all':
									subParams = {'param4': None, 'param3': 'all', 'param2': media.get('ratingKey'), 'param1': 'subtitles'}
								subs = self.getSubTitles(subParams)
								if len(subs) > 0:
									episode['subtitles'] = subs
								else:
									episode['subtitles'] = 'None'
								episodes.append(episode)
						Log.Debug('Returning %s' %(episodes))
						return episodes
					else:
						return 412	
		else:
			return 412

	''' Update settings '''
	def setSettings(self, arguments):
		# No settings to update?
		if len(arguments) == 0:
			return 412
		for f in arguments:
			# Unknown setting?
			if Dict[arguments['param2']] == None:
				return 406
			else:
				if arguments['param2'] != None:
					if Dict[arguments['param2']] == None:
						return 406									
					else:
						if arguments['param3'] == None:
							return 412
						else:
							Dict[arguments['param2']] = arguments['param3']
							return 200

	''' returns the sections '''
	def getSections(self):
		Log.Debug('Sections requested')
		rawSections = XML.ElementFromURL('http://127.0.0.1:32400/library/sections')
		Sections=[]
		for directory in rawSections:
			Section = {'key':directory.get('key'),'title':directory.get('title'),'type':directory.get('type')}
			Sections.append(Section)
		Log.Debug('Returning Sectionlist as %s' %(Sections))
		return Sections

	''' Return Section info '''
	def getSection(self, params):
		if params['param2'] != None:
			if params['param3'] == 'size':
				Log.Debug('Size requested for section %s' %(params['param2']))
				myURL = 'http://127.0.0.1:32400/library/sections/' + params['param2'] + '/all?X-Plex-Container-Start=0&X-Plex-Container-Size=1'
				try:
					section = XML.ElementFromURL(myURL)
					Log.Debug('Returning size as %s' %(section.get('totalSize')))				
					return section.get('totalSize')
				except:					
					return 404
			else:
				if params['param4'] != None:
					myURL = 'http://127.0.0.1:32400/library/sections/' + params['param2'] + '/all?X-Plex-Container-Start=' + params['param3'] + '&X-Plex-Container-Size=' + params['param4']
					rawSection = XML.ElementFromURL(myURL)
					Section=[]
					for media in rawSection:
						if params['param5'] == None:
							media = {'key':media.get('ratingKey'), 'title':media.get('title')}
							Section.append(media)
						elif params['param5'] == 'getsubs':
							# We need to get subtitle info as well here
							if params['param6'] == None:
								subParams = {'param4': None, 'param3': None, 'param2': media.get('ratingKey'), 'param1': 'subtitles'}
							if params['param6'] == 'all':
								subParams = {'param4': None, 'param3': 'all', 'param2': media.get('ratingKey'), 'param1': 'subtitles'}
							subs = self.getSubTitles(subParams)
							media = {'key':media.get('ratingKey'), 'title':media.get('title'), 'subtitles':subs}
							Section.append(media)
					Log.Debug('Returning %s' %(Section))
					return Section
				else:
					return 412	
		else:
			return 412

	''' Return subtitle information for a media '''
	def getSubTitles(self, params):
		mediaInfo = []
		myURL='http://127.0.0.1:32400/library/metadata/' + params['param2']
		if params['param2'] != None:
			try:
				bDoGetTree = True
				# Only grap subtitle here
				streams = XML.ElementFromURL(myURL).xpath('//Stream[@streamType="3"]')					
				for stream in streams:
					subInfo = {}
					if stream.get('key') == None:
						location = 'Embedded'
					elif stream.get('format') == '':
						location = 'Agent'
					else:
						location = 'Sidecar'
					if params['param3'] in {None, 'all'}:
						subInfo['key'] = stream.get('id')
						subInfo['codec'] = stream.get('codec')
						subInfo['selected'] = stream.get('selected')
						subInfo['languageCode'] = stream.get('languageCode')
						if stream.get('key') == None:
							location = 'Embedded'
						elif stream.get('format') == '':
							location = 'Agent'
						else:
							location = 'Sidecar'									
						subInfo['location'] = location
						# Get tree info, if not already done so, and if it's a none embedded srt, and we asked for all
						if params['param3'] == 'all':
							if location != None:
								if bDoGetTree:							
									MediaStreams = XML.ElementFromURL(myURL + '/tree').xpath('//MediaStream')
									bDoGetTree = False
						if params['param3'] == 'all':
							try:								
								for mediaStream in MediaStreams:				
									if mediaStream.get('id') == subInfo['key']:									
										subInfo['url'] = mediaStream.get('url')
							except:
								return 500
					mediaInfo.append(subInfo)		
			except:
				return 500
			return mediaInfo											
		else:
			return 412	

	''' Return subtitle for a media so end user can view it '''
	def getSubTitle(self, params):
		if params['param2'] != None:
			myURL='http://127.0.0.1:32400/library/metadata/' + params['param2'] + '/tree'
			if params['param3'] != None:
				try:
					srt = XML.ElementFromURL(myURL).xpath('//MediaStream[@id=' + params['param3'] + ']')
					mediaPath = srt[0].get('url')
					if 'media://' in mediaPath:
						mediaPath = os.path.join(Core.app_support_path, 'Media', 'localhost', mediaPath.replace('media://', ''))
					if 'file://' in mediaPath:
						mediaPath = mediaPath.replace('file://', '')						
					with io.open(mediaPath, 'rb') as content_file:
						content = content_file.readlines()
					showSRT = []
					for line in content:
						line = line.replace('\n', '')
						line = line.replace('\r', '')
						showSRT.append(line)
					return showSRT
				except:
					return 404
			else:
				return 412
		else:
			return 412	

	''' Delete subtitle for a media '''
	def delSubTitle(self, params):
		if params['param2'] != None:
			if params['param3'] != None:
				myURL='http://127.0.0.1:32400/library/metadata/' + params['param2'] + '/tree'
				# Grap the sub
				sub = XML.ElementFromURL(myURL).xpath('//MediaStream[@id=' + params['param3'] + ']')
				if len(sub) > 0:
					# Sub did exists, but does it have an url?
					filePath = sub[0].get('url')			
					if filePath != None:
						if filePath.startswith('media://'):
							filePath = filePath.replace('media:/', os.path.join(Core.app_support_path, 'Media', 'localhost'))
							#TODO - Agent provided sub

#							print 'filePath: ', filePath
							
							# Subtitle name
							agent, sub = filePath.split('_')

							tmp, agent = agent.split('com.')
							# Agent used
							agent = 'com.' + agent				
#							print '**** sub: ', sub, ' --- ', agent

							filePath2 = filePath.replace('Contents', 'Subtitle Contributions')
#							filePath2 = filePath2.replace('Subtitles', agent)

							filePath2, language = filePath2.split('Subtitles')
							language = language[1:3]



							print '******************************'
							print 'filePath: ', filePath
							print '******************************'



#							print 'filePath2: ', filePath2
							
#							print 'agent: ', agent

#							print 'language: ', language

#							print 'file: ', sub
	
							filePath3 = os.path.join(filePath2[:-1], agent, language, sub)

							print '******************************'
							print 'filePath3: ', filePath3
							print '******************************'



							print 'GED: ', filePath2[:-1]


#							agentXMLPath = os.path.join(filePath2[:-1], 'Contents', agent + '.xml')
							subtitlesXMLPath, tmp = filePath.split('Contents')


							agentXMLPath = os.path.join(subtitlesXMLPath, 'Contents', 'Subtitle Contributions', agent + '.xml')							

							print '******************************'
							print 'agentXMLPath: ', agentXMLPath
							print '******************************'



							subtitlesXMLPath = os.path.join(subtitlesXMLPath, 'Contents', 'Subtitles.xml')

							print '******************************'
							print 'subtitlesXMLPath: ', subtitlesXMLPath
							print '******************************'



							print 'file: ', sub

							self.DelFromXML(agentXMLPath, 'media', sub)
							self.DelFromXML(subtitlesXMLPath, 'media', sub)
				

#							agentXML = XML.ElementFromURL('"' + agentXMLPath + '"')


							# Let's refresh the media
							url = 'http://127.0.0.1:32400/library/metadata/' + params['param2'] + '/refresh&force=1'

							refresh = HTTP.Request(url, immediate=False)




# https://192-168-1-12.ebd575c9a7474c6d86b91956719f369b.plex.direct:32400/library/metadata/20/refresh&force=1

							print 'ged'

							# Nuke the actual file
							try:
								# Delete the actual file
								os.remove(filePath)
								print 'Removing: ' + filePath

								os.remove(filePath3)
								print 'Removing: ' + filePath3

#TODO: ALSO REMOVE THE SYMBLINK HERE

								# Refresh the subtitles in Plex
								self.getSubTitles(params)
							except:
								return 500


						elif filePath.startswith('file://'):
							filePath = filePath.replace('file://', '')
							try:
								# Delete the actual file
								os.remove(filePath)
								# Refresh the subtitles in Plex
								self.getSubTitles(params)
							except:
								return 500
						return  filePath
					else:
						# Not external sub
						return 406
				else:
					return 404
			else:
				# No sub ID
				return 400
		else:
			# No Media ID
			return 400


	####################################################################################################
	# Delete from an XML file
	####################################################################################################
	''' Delete from an XML file '''
	def DelFromXML(self, fileName, attribute, value):
		Log.Debug('Need to delete element with an attribute named "%s" with a value of "%s" from file named "%s"' %(attribute, value, fileName))
		with io.open(fileName, 'r') as f:
			tree = ElementTree.parse(f)
			root = tree.getroot()
			mySubtitles = root.findall('.//Subtitle')
			for Subtitles in root.findall("Language[Subtitle]"):
				for node in Subtitles.findall("Subtitle"):
					myValue = node.attrib.get(attribute)
					if myValue:
						if '_' in myValue:
							drop, myValue = myValue.split("_")
						if myValue == value:
							Subtitles.remove(node)
		tree.write(fileName, encoding='utf-8', xml_declaration=True)
		return

#**************** Handler Classes for Rest **********************

''' url /test helps devs to check that we are running '''
class testHandler(RequestHandler):
	def get(self):
		Log.Debug('Tornado recieved a test call')
		self.write("Hello, world, I'm alive")

''' Here we return the version of the plugin '''
class webToolsHandler(RequestHandler):
	#******* GET REQUEST *********
	def get(self, **params):

#		print 'THIS IS THE PARAMS: ', params
		for param in params:
			if param.startswith('_'):				
				param = None
				break
		if params['param1'] == 'version':
			self.write(webTools().getVersion())
		elif webTools().checkSecret(self.request.headers):
			if params['param1'] == 'test':
				self.write('test')
			elif params['param1'] == 'settings':
				response = webTools().getSettings(params)
				if response == 406:
					self.clear()
					self.set_status(406)
					self.finish("<html><body>Unknown setting</body></html>")
				else:
					self.write(webTools().getSettings(params))
			elif params['param1'] == 'sections':
				response = webTools().getSections()
				if response == 406:
					self.clear()
					self.set_status(406)
					self.finish("<html><body>Unknown setting</body></html>")
				else:
					self.write(json_encode(response))
			elif params['param1'] == 'section':
				response = webTools().getSection(params)			
				if response == 412:
					self.clear()
					self.set_status(412)
					self.finish("<html><body>Missing section key</body></html>")
				elif response == 404:
					self.clear()
					self.set_status(404)
					self.finish("<html><body>section not found</body></html>")
				else:
					self.write(json_encode(response))
			elif params['param1'] == 'show':
				response = webTools().getShow(params)			
				if response == 412:
					self.clear()
					self.set_status(412)
					self.finish("<html><body>Missing parameters</body></html>")
				elif response == 404:
					self.clear()
					self.set_status(404)
					self.finish("<html><body>show not found</body></html>")
				else:
					self.write(json_encode(response))
			elif params['param1'] == 'subtitles':
				response = webTools().getSubTitles(params)
				if response == 412:
					self.clear()
					self.set_status(412)
					self.finish("<html><body>Missing media key</body></html>")
				elif response == 404:
					self.clear()
					self.set_status(404)
					self.finish("<html><body>Media not found</body></html>")
				elif response == 400:
					self.clear()
					self.set_status(400)
					self.finish("<html><body>Unknown 3 parameter</body></html>")
				else:
					self.write(json_encode(response))
			elif params['param1'] == 'subtitle':
				print 'Hello World'
				response = webTools().getSubTitle(params)
				if response == 412:
					self.clear()
					self.set_status(412)
					self.finish("<html><body>Missing media key or subtitle Id</body></html>")
				elif response == 404:
					self.clear()
					self.set_status(404)
					self.finish("<html><body>Subtitle not found</body></html>")
				elif response == 500:
					self.clear()
					self.set_status(500)
					self.finish("<html><body>We failed</body></html>")
				else:
					self.write(json_encode(response))
			else:
				# Return a not found error
				raise HTTPError(404)
		else:
			# Return a not found error
			raise HTTPError(401)

	#******* PUT REQUEST *********
	def put(self, **params):
		if webTools().checkSecret(self.request.headers):
			if params['param1'] == 'test':
				self.write('test')
			elif params['param1'] == 'settings':
				response = webTools().setSettings(params)
				if response == 200:
					self.clear()
					self.set_status(200)
				elif response == 412:
					self.clear()
					self.set_status(412)
					self.finish("<html><body>Missing settings to update</body></html>")
				elif response == 406:
					self.clear()
					self.set_status(406)
					self.finish("<html><body>Tried to update unknown setting</body></html>")					
			else:
				# Return a not found error
				raise HTTPError(404)
		else:
			# Return a not found error
			raise HTTPError(401)

	#******* POST REQUEST *********
	def post(self, **params):
		raise HTTPError(404)

	#******* DELETE REQUEST *********
	def delete(self, **params):
		if params['param1'] == 'subtitle':
			response = webTools().delSubTitle(params)
			if response == 400:
				self.clear()
				self.set_status(400)
				self.finish("<html><body>Bad request...maybe missing a parameter here?</body></html>")
			elif response == 404:
				self.clear()
				self.set_status(404)
				self.finish("<html><body>Not found</body></html>")
			elif response == 406:
				self.clear()
				self.set_status(406)
				self.finish("<html><body>Hmmm....This is invalid, and most likely due to trying to delete an embedded sub :-)</body></html>")
			else:
				self.write(json_encode(response))
		else:
			self.clear()
			self.set_status(404)
			self.finish("<html><body>Unknown call</body></html>")
		
# The default handler is the test handler
handlers = [(r'/test', testHandler),
						(r"/webtools/(?P<param1>[^\/]+)/?(?P<param2>[^\/]+)?/?(?P<param3>[^\/]+)?/?(?P<param4>[^\/]+)?/?(?P<param5>[^\/]+)?/?(?P<param6>[^\/]+)?/?(?P<param7>[^\/]+)?/?(?P<param8>[^\/]+)?", webToolsHandler)
]

#********* Tornado itself *******************
''' Start the actual instance of tornado '''
def start_tornado():
	application = Application(handlers)
	http_server = HTTPServer(application)
	# Set web server port to the setting in the channel prefs
	port = int(Prefs['WEB_Port'])	
	http_server.listen(port)
	Log.Debug('Starting tornado on port %s' %(port))
	IOLoop.instance().start()
	Log.Debug('Shutting down tornado')

''' Stop the actual instance of tornado '''
def stopWeb():
	IOLoop.instance().add_callback(IOLoop.instance().stop)
	Log.Debug('Asked Tornado to exit')

''' Main call '''
def startWeb():

	stopWeb()

	# Path to http directory in the bundle, that we need to serve
	actualPath =  {'path': os.path.join(Core.app_support_path, 'Plug-ins', NAME + '.bundle', 'http')}
	rootpath = (r'/(.*)', StaticFileHandler, actualPath)
	global handlers
	handlers.append(rootpath)
	Log.Debug('tornado is handling the following URI: %s' %(handlers))
	t = threading.Thread(target=start_tornado)
	t.start()

