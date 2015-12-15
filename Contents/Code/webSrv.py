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

#from tornado.web import RequestHandler, StaticFileHandler, Application, HTTPError
from tornado.web import *
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.escape import json_encode, xhtml_escape
from plextvhelper import plexTV


# Migrated to new way
from git import git
from logs import logs
from pms import pms
from settings import settings


import io
import threading
from datetime import date
from random import randint
import json
from xml.etree import ElementTree
from itertools import islice



#Legacy
from OLDinstall import install
from OLDupdater import updater




# TODO from importlib import import_module



# Path to http folder within the bundle
ACTUALPATH =  os.path.join(Core.app_support_path, 'Plug-ins', NAME + '.bundle', 'http')

#************** webTools functions ******************************
''' Here we have the supported functions '''
class webTools(object):
	''' Return version number, and other info '''
	def getVersion(self):
		retVal = {'version': VERSION, 
						'PasswordSet': Dict['pwdset'],
						'PlexTVOnline': plexTV().auth2myPlex()}
		Log.Debug('Version requested, returning ' + str(retVal))
		return retVal

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
		mySetting['debug'] = (Dict['debug'] == 'true')
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
							'''
Here we look at an agent provided subtitle, so this part of the function 
has been crippled on purpose
							'''
							filePath = filePath.replace('media:/', os.path.join(Core.app_support_path, 'Media', 'localhost'))
							# Subtitle name
							agent, sub = filePath.split('_')
							tmp, agent = agent.split('com.')
							# Agent used
							agent = 'com.' + agent				
							filePath2 = filePath.replace('Contents', 'Subtitle Contributions')
							filePath2, language = filePath2.split('Subtitles')
							language = language[1:3]	
							filePath3 = os.path.join(filePath2[:-1], agent, language, sub)

							''' This is removed from the code, due to the fact, that Plex will re-download right after the deletion

							subtitlesXMLPath, tmp = filePath.split('Contents')
							agentXMLPath = os.path.join(subtitlesXMLPath, 'Contents', 'Subtitle Contributions', agent + '.xml')							
							subtitlesXMLPath = os.path.join(subtitlesXMLPath, 'Contents', 'Subtitles.xml')
							self.DelFromXML(agentXMLPath, 'media', sub)
							self.DelFromXML(subtitlesXMLPath, 'media', sub)
							agentXML = XML.ElementFromURL('"' + agentXMLPath + '"')
							#Let's refresh the media
							url = 'http://127.0.0.1:32400/library/metadata/' + params['param2'] + '/refresh&force=1'
							refresh = HTTP.Request(url, immediate=False)

							# Nuke the actual file
							try:
								# Delete the actual file
								os.remove(filePath)
								print 'Removing: ' + filePath

								os.remove(filePath3)
								print 'Removing: ' + filePath3
								# Refresh the subtitles in Plex
								self.getSubTitles(params)
							except:
								return 500
							'''

							retValues = {}
							retValues['FilePath']=filePath3
							retValues['SymbLink']=filePath
							return retValues
						elif filePath.startswith('file://'):
							filePath = filePath.replace('file://', '')
							try:
								# Delete the actual file
								os.remove(filePath)
								# Refresh the subtitles in Plex....Takes some time, but better now, than when user wanna watch a movie
								self.getSubTitles(params)
								return 'Deleted file : ' + filePath
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

class BaseHandler(RequestHandler):
	def get_current_user(self):
		return self.get_secure_cookie(NAME)

''' handler to force TLS '''
class ForceTSLHandler(RequestHandler):
	def get(self):
		''' This is sadly up hill, due to the old version of Tornado used :-( '''
		# Grap the host requested
		host, port = self.request.headers['Host'].split(':')
		newUrl = 'https://' + host + ':' + Prefs['WEB_Port_https'] + '/login'
		self.redirect(newUrl, permanent=True)

''' If user didn't enter the full path '''
class idxHandler(BaseHandler):
	@authenticated
	def get(self):
		self.render(ACTUALPATH + "/index.html")

''' If user didn't enter the full path '''
class LogoutHandler(BaseHandler):
	@authenticated
	def get(self):
		self.clear_cookie(NAME)
		self.redirect('/')

class LoginHandler(BaseHandler):
	def get(self):
		self.render(ACTUALPATH + "/login.html", next=self.get_argument("next","/"))

	def post(self):
		global AUTHTOKEN
		# Let's start by checking if the server is online
		if plexTV().auth2myPlex():
			token = ''
			try:
				# Authenticate
				retVal = plexTV().isServerOwner(plexTV().login(self))
				self.clear()
				if retVal == 0:
					# All is good
					self.allow()
					self.redirect('/')
				elif retVal == 1:
					# Server not found				
					self.set_status(404)
				elif retVal == 2:
					# Not the owner
					self.set_status(403)
				else:
					# Unknown error
					self.set_status(403)
			except Ex.HTTPError, e:
				self.clear()
				self.set_status(e.code)
				self.finish(e)
				return self
		else:
			# Server is offline
			if Dict['password'] == '':
				Dict['password'] = self.get_argument("pwd")
				Dict['pwdset'] = True
				Dict.Save
				self.allow()
				self.redirect('/')
			elif Dict['password'] == self.get_argument("pwd"):
				self.allow()
				self.redirect('/')
			elif Dict['password'] != self.get_argument("pwd"):
					self.clear()
					self.set_status(401)

	def allow(self):
		self.set_secure_cookie(NAME, Hash.MD5(Dict['SharedSecret']+Dict['password']), expires_days = None)

class versionHandler(RequestHandler):
	def get(self, **params):
		self.set_header('Content-Type', 'application/json; charset=utf-8')
		self.write(webTools().getVersion())


class webTools2Handler(BaseHandler):
	#******* GET REQUEST *********
	@authenticated
#	print '********** AUTH DISABLED WebSRV WebTools2 GET'

	# Get Request
	def get(self, **params):
		module = self.get_argument('module', 'missing')
		if module == 'missing':
			self.clear()
			self.set_status(404)
			self.finish("<html><body>Missing function call</body></html>")
			return
		else:
			Log.Debug('Recieved a get call for module: ' + module)
	
#TODO

#			import sys
#			sys.path.append('/share/CACHEDEV1_DATA/.qpkg/PlexMediaServer/Library/Plex Media Server/Plug-ins/WebTools.bundle/Contents/Code')
#			mod = import_module(module)
#			modClass = getattr(mod, module)
#			reqprocess = getattr(modClass, 'reqprocess')

			if module == 'git':			
				self = git().reqprocess(self)
			elif module == 'logs':
				self = logs().reqprocess(self)
			elif module == 'pms':
				self = pms().reqprocess(self)
			elif module == 'settings':
				self = settings().reqprocess(self)
			else:
				self.clear()
				self.set_status(412)
				self.finish("<html><body>Unknown module call</body></html>")
				return

	#******* POST REQUEST *********
	@authenticated
#	print '********** AUTH DISABLED WebSRV WebTools2 POST'

	def post(self, **params):
		module = self.get_argument('module', 'missing')
		if module == 'missing':
			self.clear()
			self.set_status(404)
			self.finish("<html><body>Missing function call</body></html>")
			return
		else:
			Log.Debug('Recieved a post call for module: ' + module)
			if module == 'logs':			
				self = logs().reqprocessPost(self)
			else:
				self.clear()
				self.set_status(412)
				self.finish("<html><body>Unknown module call</body></html>")
				return

	#******* DELETE REQUEST *********
	@authenticated
#	print '********** AUTH DISABLED WebSRV WebTools2 DELETE'

	def delete(self, **params):
		module = self.get_argument('module', 'missing')
		if module == 'missing':
			self.clear()
			self.set_status(404)
			self.finish("<html><body>Missing function call</body></html>")
			return
		else:
			Log.Debug('Recieved a delete call for module: ' + module)
			if module == 'pms':			
				self = pms().reqprocessDelete(self)
			else:
				self.clear()
				self.set_status(412)
				self.finish("<html><body>Unknown module call</body></html>")
				return

	#******* PUT REQUEST *********
	@authenticated
#	print '********** AUTH DISABLED WebSRV WebTools2 PUT'

	def put(self, **params):
		module = self.get_argument('module', 'missing')
		if module == 'missing':
			self.clear()
			self.set_status(404)
			self.finish("<html><body>Missing function call</body></html>")
			return
		else:
			Log.Debug('Recieved a delete call for module: ' + module)
			if module == 'settings':			
				self = settings().reqprocessPUT(self)
			else:
				self.clear()
				self.set_status(412)
				self.finish("<html><body>Unknown module call</body></html>")
				return



		
class webToolsHandler(BaseHandler):
	#******* GET REQUEST *********
	@authenticated
#	print 'AUTH DISABLED for WebTools GET'
	def get(self, **params):
#		print 'THIS IS THE PARAMS: ', params
		for param in params:
			if param.startswith('_'):				
				param = None
				break
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
				self.set_header('Content-Type', 'application/json; charset=utf-8')
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
				self.set_header('Content-Type', 'application/json; charset=utf-8')
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
				self.set_header('Content-Type', 'application/json; charset=utf-8')
				self.write(json_encode(response))
		elif params['param1'] == 'subtitle':
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
				self.set_header('Content-Type', 'application/json; charset=utf-8')
				self.write(json_encode(response))

		# Call for updates
		elif params['param1'] == 'update':
			if params['param2'] == 'all':
				if params['param3'] == None:
					Log.Debug('Missing Param3 for update (Owner)')
					raise HTTPError(510)
				if params['param4'] == None:
					Log.Debug('Missing Param4 for update (Git Repo)')
					raise HTTPError(510)
				self.set_header('Content-Type', 'application/json; charset=utf-8')
				self.write(json_encode(updater().getlatestinfo(params['param3'], params['param4'], True, True)))
			elif params['param2'] != None:
				if params['param3'] == None:
					Log.Debug('Missing Param3 for update (Git Repo)')
					raise HTTPError(510)
				self.set_header('Content-Type', 'application/json; charset=utf-8')
				self.write(json_encode(updater().getlatestinfo(params['param2'], params['param3'], True)))
			else:
				raise HTTPError(510)
		else:
			# Return a not found error
			raise HTTPError(404)

	#******* PUT REQUEST *********
	@authenticated
	def put(self, **params):
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

	#******* POST REQUEST *********
	@authenticated
	def post(self, **params):
#		print 'THIS IS THE PARAMS: ', params
		if params['param1'] == 'password':
			if params['param2'] == Dict['password']:
				if params['param3'] != None:
					Dict['password'] = params['param3']
					Dict.Save
				else:
					self.clear()
					self.set_status(400)
					self.finish("<html><body>Bad New password</body></html>")
			else:
				self.clear()
				self.set_status(401)
				self.finish("<html><body>Bad password</body></html>")
		elif params['param1'] == 'logs':
			Log.Debug('FrontEnd: ' + params['param2'])
		else:
			raise HTTPError(404)

	#******* DELETE REQUEST *********
	@authenticated
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

handlers = [(r"/login", LoginHandler),
						(r"/logout", LogoutHandler),
						(r"/webtools/version", versionHandler),
						(r'/', idxHandler),
						(r'/index.html', idxHandler),
						(r"/webtools2*$", webTools2Handler),



						(r"/webtools/(?P<param1>[^\/]+)/?(?P<param2>[^\/]+)?/?(?P<param3>[^\/]+)?/?(?P<param4>[^\/]+)?/?(?P<param5>[^\/]+)?/?(?P<param6>[^\/]+)?/?(?P<param7>[^\/]+)?/?(?P<param8>[^\/]+)?", webToolsHandler),
						(r'/(.*)', StaticFileHandler, {'path': ACTUALPATH})
]

if Prefs['Force_SSL']:
	httpHandlers = [(r"/login", ForceTSLHandler),
									(r"/logout", LogoutHandler),
									(r"/webtools/version", ForceTSLHandler),
									(r'/', ForceTSLHandler),
									(r'/index.html', ForceTSLHandler),
									(r"/webtools2*$", webTools2Handler),
									(r"/webtools/(?P<param1>[^\/]+)/?(?P<param2>[^\/]+)?/?(?P<param3>[^\/]+)?/?(?P<param4>[^\/]+)?/?(?P<param5>[^\/]+)?/?(?P<param6>[^\/]+)?/?(?P<param7>[^\/]+)?/?(?P<param8>[^\/]+)?", ForceTSLHandler)]

else:
	httpHandlers = handlers

httpsHandlers = handlers

#********* Tornado itself *******************
''' Start the actual instance of tornado '''
def start_tornado():
	myCookie = Hash.MD5(Dict['SharedSecret'] + NAME)

	settings = {"cookie_secret": "__" + myCookie + "__",
							"login_url": "/login"}

	application = Application(httpHandlers, **settings)
	applicationTLS = Application(httpsHandlers, **settings)
	http_server = HTTPServer(application)
	# Use our own certificate for TLS
	http_serverTLS = HTTPServer(applicationTLS, 
													ssl_options={
																			"certfile": os.path.join(Core.bundle_path, 'Contents', 'Code', 'Certificate', 'WebTools.crt'),
																			"keyfile": os.path.join(Core.bundle_path, 'Contents', 'Code', 'Certificate', 'WebTools.key')})


	# Set web server port to the setting in the channel prefs
	port = int(Prefs['WEB_Port_http'])
	ports = int(Prefs['WEB_Port_https'])	
	http_server.listen(port)
	http_serverTLS.listen(ports)

	Log.Debug('Starting tornado on ports %s and %s' %(port, ports))
	IOLoop.instance().start()
	Log.Debug('Shutting down tornado')

''' Stop the actual instance of tornado '''
def stopWeb():
	IOLoop.instance().add_callback(IOLoop.instance().stop)
	Log.Debug('Asked Tornado to exit')

''' Main call '''
def startWeb(secretKey):
	global SECRETKEY
	# Set the secret key for use by other calls in the future maybe?
	SECRETKEY = secretKey
	stopWeb()
	Log.Debug('tornado is handling the following URI: %s' %(handlers))
	t = threading.Thread(target=start_tornado)
	t.start()

