######################################################################################################################
#	Playlist module unit					
#
#	Author: dane22, a Plex Community member
#
# 	A WebTools module for handling playlists
#
######################################################################################################################
import time, io, json, datetime, re
from misc import misc
from plextvhelper import plexTV
from uuid import uuid4

#TODO: Remove when Plex framework allows token in the header. Also look at delete and list method
import urllib2
from xml.etree import ElementTree
#import requests
#TODO End


GET = ['LIST', 'DOWNLOAD']
PUT = []
POST = ['COPY', 'IMPORT']
DELETE = ['DELETE']

EXCLUDE = 'excludeElements=Actor,Collection,Country,Director,Genre,Label,Mood,Producer,Similar,Writer,Role&excludeFields=summary,tagline'

class playlistsV3(object):
	# Defaults used by the rest of the class
	@classmethod
	def init(self):
		self.getListsURL = misc.GetLoopBack() + '/playlists/all'

	''' This metode will import a playlist. '''
	@classmethod
	def IMPORT(self, req, *args):
		# Just init of internal stuff		
		sName = None
		sType = None
		sSrvId = None
		bSameSrv = False
		
		# Payload Upload file present?
		if not 'localFile' in req.request.files:
			req.clear()
			req.set_status(412)
			req.finish('Missing upload file parameter named localFile from the payload')			
		else:
			localFile = req.request.files['localFile'][0]['body']			
		try:									
			# Make into seperate lines
			lines = localFile.split('\n')
			# Start by checking if we have a valid playlist file
			if lines[0] != '#EXTM3U':
				Log.Error('Import file does not start with the line: #EXTM3U')
				req.clear()
				req.set_status(406)			
				req.finish('Seems like we are trying to import a file that is not a playlist!')
			# Let's check if it's one of ours
			bOurs = (lines[1] == '#Written by WebTools for Plex')
			if bOurs:
				# Placeholder for items to import
				items = {}
				Log.Debug('Import file was ours')
				sName = lines[2].split(':')[1][1:]
				Log.Debug('Playlist name is %s' %sName)				
				sType = lines[3].split(':')[1][1:]
				Log.Debug('Playlist type is %s' %sType)
				sSrvId = lines[4].split(':')[1][1:]
				Log.Debug('ServerId this playlist belongs to is %s' %sSrvId)					
				thisServerID = XML.ElementFromURL(misc.GetLoopBack() + '/identity').get('machineIdentifier')
				Log.Debug('Current Server id is %s' %thisServerID)
				bSameSrv = (thisServerID == sSrvId)
				lineNo = 5				
				try:
					for line in lines[5:len(lines):3]:						
						media = json.loads(lines[lineNo][1:])
						id = media['Id']
						item = {}
						item['ListId'] = media['ListId']
						item['LibraryUUID'] = media['LibraryUUID']
						lineNo +=1						
						media = lines[lineNo][8:].split(',', 1)										
						item['title'] = media[1].split('-', 1)[1][1:]
						lineNo +=1						
						item['fileName'] = lines[lineNo]						
						items[id] = item
						lineNo +=1
				except IndexError:
					pass
				except Exception, e:										
					Log.Exception('Exception happened in IMPORT was %s' %(str(e)))
					pass			
			finalItems = {}
			for item in items:
				if checkItemIsValid(item, items[item]['title'], sType):
					finalItem = {}
					finalItem['id'] = id
					finalItem['LibraryUUID'] = str(items[item]['LibraryUUID'])
					finalItem['title'] = items[item]['title']						
					finalItems[items[item]['ListId']] = finalItem
				else:					
					Log.Debug('Could not item with a title of %s' %items[item]['title'])
					result = searchForItemKey(items[item]['title'], sType)
					if result != None:					
						finalItem = {}
						finalItem['id'] = result[0]
						finalItem['LibraryUUID'] = result[1]								
						finalItem['title'] = items[item]['title']						
						finalItems[items[item]['ListId']] = finalItem
					else:
						Log.Error('Item %s was not found' %items[item]['title'])
									
			print finalItems
			
		except Exception, e:
			Log.Exception('Exception happened in Playlist import was: %s' %(str(e)))
			req.clear()
			req.set_status(500)
			req.finish('Exception happened in Playlist import was: %s' %(str(e)))

		return				


	''' This metode will copy a playlist. between users '''
	@classmethod
	def COPY(self, req, *args):
		users = None
		# Start by getting the key of the PlayList
		if args != None:
			# We got additional arguments
			if len(args) > 0:
				# Get them in lower case
				arguments = [item.lower() for item in list(args)[0]]
			else:
				Log.Critical('Missing Arguments')
				req.clear()
				req.set_status(412)			
				req.finish('Missing Arguments')
			# Get playlist Key
			if 'key' in arguments:
				# Get key of the user
				key = arguments[arguments.index('key') +1]
			else:
				Log.Error('Missing key of playlist')
				req.clear()
				req.set_status(412)			
				req.finish('Missing key of playlist')
			# Get UserFrom
			if 'userfrom' in arguments:
				# Get the userfrom
				userfrom = arguments[arguments.index('userfrom') +1]
			else:
				# Copy from the Owner
				userfrom = None
			# Get UserTo
			if 'userto' in arguments:
				# Get the userto
				userto = arguments[arguments.index('userto') +1]
			else:
				Log.Error('Missing target user of playlist')
				req.clear()
				req.set_status(412)			
				req.finish('Missing targetuser of playlist')
			# Get user list, among with access token
			users = plexTV().getUserList()
			# Get the playlist that needs to be copied
			url = misc.GetLoopBack() + '/playlists/' + key + '/items'
			if userfrom == None:
				# Get it from the owner
				playlist = XML.ElementFromURL(url)
			else:
				#We need to logon as specified user
				try:
					# Get user playlist
					#TODO Change to native framework call, when Plex allows token in header
					opener = urllib2.build_opener(urllib2.HTTPHandler)
					request = urllib2.Request(url)
					request.add_header('X-Plex-Token', users[userfrom]['accessToken'])
					response = opener.open(request).read()
					playlist = XML.ElementFromString(response)
				except Ex.HTTPError, e:
					Log.Exception('HTTP exception  when downloading a playlist for the owner was: %s' %(e))
					req.clear()
					req.set_status(e.code)			
					req.finish(str(e))
				except Exception, e:
					Log.Exception('Exception happened when downloading a playlist for the user was: %s' %(str(e)))
					req.clear()
					req.set_status(500)			
					req.finish('Exception happened when downloading a playlist for the user was: %s' %(str(e)))
			# Now walk the playlist, and do a lookup for the items, in order to grab the librarySectionUUID
			jsonItems = {}
			playlistType = playlist.get('playlistType')
			playlistTitle = playlist.get('title')
			playlistSmart = (playlist.get('smart') == 1)
			for item in playlist:
				itemKey = item.get('ratingKey')
				xmlUrl = misc.GetLoopBack() + '/library/metadata/' + itemKey + '?' + EXCLUDE				
				UUID = XML.ElementFromURL(misc.GetLoopBack() + '/library/metadata/' + itemKey).get('librarySectionUUID')
				if UUID in jsonItems:
					jsonItems[UUID].append(itemKey)
				else:
					jsonItems[UUID] = []
					jsonItems[UUID].append(itemKey)
			Log.Debug('Got a playlist that looks like:')
			Log.Debug(json.dumps(jsonItems))
			# So we got all the info needed now from the source user, now time for the target user
			try:
				#TODO Change to native framework call, when Plex allows token in header
				urltoPlayLists = misc.GetLoopBack() + '/playlists'
				opener = urllib2.build_opener(urllib2.HTTPHandler)
				request = urllib2.Request(urltoPlayLists)
				request.add_header('X-Plex-Token', users[userto]['accessToken'])
				response = opener.open(request).read()
				playlistto = XML.ElementFromString(response)
			except Ex.HTTPError, e:
				Log.Exception('HTTP exception when downloading a playlist for the owner was: %s' %(e))
				req.clear()
				req.set_status(e.code)			
				req.finish(str(e))
			except Exception, e:
				Log.Exception('Exception happened when downloading a playlist for the user was: %s' %(str(e)))
				req.clear()
				req.set_status(500)			
				req.finish('Exception happened when downloading a playlist for the user was: %s' %(str(e)))
			# So we got the target users list of playlists, and if the one we need to copy already is there, we delete it
			for itemto in playlistto:
				if playlistTitle == itemto.get('title'):
					keyto = itemto.get('ratingKey')
					deletePlayLIstforUsr(req, keyto, users[userto]['accessToken'])
			# Make url for creation of playlist
			targetFirstUrl = misc.GetLoopBack() + '/playlists?type=' + playlistType + '&title=' + String.Quote(playlistTitle) + '&smart=0&uri=library://'
			counter = 0
			for lib in jsonItems:
				if counter < 1:
					targetFirstUrl += lib + '/directory//library/metadata/'
					medias = ','.join(map(str, jsonItems[lib])) 
					targetFirstUrl += String.Quote(medias)
					# First url for the post created, so send it, and grab the response
					try:
						opener = urllib2.build_opener(urllib2.HTTPHandler)
						request = urllib2.Request(targetFirstUrl)
						request.add_header('X-Plex-Token', users[userto]['accessToken'])
						request.get_method = lambda: 'POST'
						response = opener.open(request).read()
						ratingKey = XML.ElementFromString(response).xpath('Playlist/@ratingKey')[0]
					except Exception, e:
						Log.Exception('Exception creating first part of playlist was: %s' %(str(e)))
					counter += 1
				else:
					# Remaining as put
					medias = ','.join(map(str, jsonItems[lib])) 
					targetSecondUrl = misc.GetLoopBack() + '/playlists/' + ratingKey + '/items?uri=library://' + lib + '/directory//library/metadata/' + String.Quote(medias)
					opener = urllib2.build_opener(urllib2.HTTPHandler)
					request = urllib2.Request(targetSecondUrl)
					request.add_header('X-Plex-Token', users[userto]['accessToken'])
					request.get_method = lambda: 'PUT'
					opener.open(request)
		else:
			Log.Critical('Missing Arguments')
			req.clear()
			req.set_status(412)			
			req.finish('Missing Arguments')

	''' This metode will download a playlist. accepts a user parameter '''
	@classmethod
	def DOWNLOAD(self, req, *args):
		try:
			user = None
			if args != None:
				# We got additional arguments
				if len(args) > 0:
					# Get them in lower case
					arguments = [item.lower() for item in list(args)[0]]
					if 'user' in arguments:
						# Get key of the user
						user = arguments[arguments.index('user') +1]
				# So now user is either none (Owner) or a keyId of a user
				# Now lets get the key of the playlist
				if 'key' in arguments:
					# Get key of the user
					key = arguments[arguments.index('key') +1]
					url = misc.GetLoopBack() + '/playlists/' + key + '/items' + '?' + EXCLUDE
				else:
					Log.Error('Missing key of playlist')
					req.clear()
					req.set_status(412)			
					req.finish('Missing key of playlist')
				try:
					Log.Info('downloading playlist with ID: %s' %key)
					if user == None:
						# Get playlist from the owner					
						playlist = XML.ElementFromURL(url)
					else:
						# Get Auth token for user
						try:
							# Get user list, among with their access tokens
							users = plexTV().getUserList()	
							#TODO Change to native framework call, when Plex allows token in header
							opener = urllib2.build_opener(urllib2.HTTPHandler)
							request = urllib2.Request(url)
							request.add_header('X-Plex-Token', users[user]['accessToken'])
							response = opener.open(request).read()
							playlist = XML.ElementFromString(response)
						except Ex.HTTPError, e:
							Log.Exception('HTTP exception when downloading a playlist for the owner was: %s' %(e))
							req.clear()
							req.set_status(e.code)			
							req.finish(str(e))
						except Exception, e:
							Log.Exception('Exception happened when downloading a playlist for the user was: %s' %(str(e)))
							req.clear()
							req.set_status(e.code)			
							req.finish('Exception happened when downloading a playlist for the user was: %s' %(str(e)))
					# Get title of playlist
					title = playlist.get('title')
					playListType = playlist.get('playlistType')
					# Replace invalid caracters for a filename with underscore
					fileName = re.sub('[\/[:#*?"<>|]', '_', title).strip() + '.m3u8'
					# Prep the download http headers
					req.set_header ('Content-Disposition', 'attachment; filename=' + fileName)
					req.set_header('Cache-Control', 'no-cache')
					req.set_header('Pragma', 'no-cache')
					req.set_header('Content-Type', 'application/text/plain')
					#start writing
					req.write(unicode('#EXTM3U') + '\n')
					req.write(unicode('#Written by WebTools for Plex') + '\n')
					req.write(unicode('#Playlist name: ' + title) + '\n')
					req.write(unicode('#Playlist type: ' + playListType) + '\n')
					req.write(unicode('#Server Id: ' + XML.ElementFromURL(misc.GetLoopBack() + '/identity').get('machineIdentifier')) + '\n')
					# Lets grap the individual items
					for item in playlist:
						# Get the Library UUID
						url = misc.GetLoopBack() + '/library/metadata/' + item.get('ratingKey') + '?' + EXCLUDE											
						libraryUUID = XML.ElementFromURL(url).get('librarySectionUUID')							
						req.write(unicode('#{"Id":' + item.get('ratingKey') + ', "ListId":' + item.get('playlistItemID') + ', "LibraryUUID":"' + libraryUUID + '"}\n'))
						row = '#EXTINF:'
						# Get duration
						try:
							duration = int(item.get('duration'))/1000
						except:
							duration = -1
							pass
						row = row + str(duration) + ','
						# Audio List
						if playListType == 'audio':
							try:
								if item.get('originalTitle') == None:
									row = row + item.get('grandparentTitle').replace(' - ', ' ') + ' - ' + item.get('title').replace(' - ', ' ')
								else:
									row = row + item.get('originalTitle').replace(' - ', ' ') + ' - ' + item.get('title').replace(' - ', ' ')								
							except Exception, e:
								Log.Exception('Exception digesting an audio entry was %s' %(str(e)))
								pass
						# Video
						elif playListType == 'video':
							try:
								entryType =  item.get('type')
								if entryType == 'movie':
									# Movie
									row = row + 'movie' + ' - ' + item.get('title')
								else:
									# Show
									row = row + 'show' + ' - ' + item.get('title')
							except Exception, e:
								Log.Exception('Exception happened when digesting the line for Playlist was %s' %(str(e)))
								pass
						# Pictures
						else:
							row = row + item.get('title').replace(' - ', ' ')
						# Add file path
						row = row + '\n' + item.xpath('Media/Part/@file')[0]
						req.write(unicode(row) + '\n')
					req.set_status(200)
					req.finish()
				except Ex.HTTPError, e:
					Log.Exception('HTTP exception  when downloading a playlist for the owner was: %s' %(e))
					req.clear()
					req.set_status(e.code)			
					req.finish(str(e))
				except Exception, e:
					Log.Exception('Exception happened when downloading a playlist for the owner was: %s' %(str(e)))
					req.clear()
					req.set_status(e.code)			
					req.finish('Exception happened when downloading a playlist for the owner was: %s' %(str(e)))
		except Exception, e:
			Log.Exception('Fatal error happened in playlists.download: ' + str(e))
			req.clear()
			req.set_status(e.code)			
			req.finish('Fatal error happened in playlists.download: %s' %(str(e)))
	

	''' This metode will delete a playlist. accepts a user parameter '''
	@classmethod
	def DELETE(self, req, *args):
		try:
			user = None
			if args != None:
				# We got additional arguments
				if len(args) > 0:
					# Get them in lower case
					arguments = [item.lower() for item in list(args)[0]]
					if 'user' in arguments:
						# Get key of the user
						user = arguments[arguments.index('user') +1]
				# So now user is either none (Owner) or a keyId of a user
				# Now lets get the key of the playlist
				if 'key' in arguments:
					# Get key of the user
					key = arguments[arguments.index('key') +1]
					url = misc.GetLoopBack() + '/playlists/' + key
				else:
					Log.Error('Missing key of playlist')
					req.clear()
					req.set_status(412)			
					req.finish('Missing key of playlist')
			if user == None:
				try:
					# Delete playlist from the owner					
					Log.Info('Deleting playlist with ID: %s' %key)		
					HTTP.Request(url, cacheTime=0, immediate=True, method="DELETE")
				except Ex.HTTPError, e:
					Log.Exception('HTTP exception  when deleting a playlist for the owner was: %s' %(e))
					req.clear()
					req.set_status(e.code)			
					req.finish(str(e))
				except Exception, e:
					Log.Exception('Exception happened when deleting a playlist for the owner was: %s' %(str(e)))
					req.clear()
					req.set_status(500)			
					req.finish('Exception happened when deleting a playlist for the owner was: %s' %(str(e)))
			else:
				# We need to logon as a user in order to nuke the playlist
				try:
					# Get user list, among with their access tokens
					users = plexTV().getUserList()
					# Detele the playlist	
					deletePlayLIstforUsr(req, key, users[user]['accessToken'])
				except Ex.HTTPError, e:
					Log.Exception('HTTP exception  when deleting a playlist for the owner was: %s' %(e))
					req.clear()
					req.set_status(e.code)			
					req.finish(str(e))
				except Exception, e:
					Log.Exception('Exception happened when deleting a playlist for the user was: %s' %(str(e)))
					req.clear()
					req.set_status(500)			
					req.finish('Exception happened when deleting a playlist for the user was: %s' %(str(e)))				
		except Exception, e:
			Log.Exception('Fatal error happened in playlists.delete: ' + str(e))
			req.clear()
			req.set_status(500)			
			req.finish('Fatal error happened in playlists.delete: %s' %(str(e)))

	''' This metode will return a list of playlists. accepts a user parameter '''
	@classmethod
	def LIST(self, req, *args):
		try:
			user = None
			if args != None:
				# We got additional arguments
				if len(args) > 0:
					# Get them in lower case
					arguments = [item.lower() for item in list(args)[0]]
					if 'user' in arguments:
						# Get key of the user
						user = arguments[arguments.index('user') +1]
			# So now user is either none or a keyId
			if user == None:
				playlists = XML.ElementFromURL(self.getListsURL)
			else:
				#Darn....Hard work ahead..We have to logon as another user here :-(
				users = plexTV().getUserList()	
				myHeader = {}
				myHeader['X-Plex-Token'] = users[user]['accessToken']
				#TODO Change to native framework call, when Plex allows token in header
				request = urllib2.Request(self.getListsURL, headers=myHeader)
				playlists = XML.ElementFromString(urllib2.urlopen(request).read())
				#playlists = XML.ElementFromURL(self.getListsURL, headers=myHeader)
			result = {}
			for playlist in playlists:
				id = playlist.get('ratingKey')
				result[id] = {}
				result[id]['title'] = playlist.get('title')
				result[id]['summary'] = playlist.get('summary')
				result[id]['smart'] = playlist.get('smart')
				result[id]['playlistType'] = playlist.get('playlistType')
			req.set_status(200)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish(json.dumps(result))
		except Exception, e:
			Log.Exception('Fatal error happened in playlists.list: ' + str(e))
			req.clear()
			req.set_status(500)			
			req.finish('Fatal error happened in playlists.list: %s' %(str(e)))

	''' Get the relevant function and call it with optinal params '''
	@classmethod
	def getFunction(self, metode, req):		
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


#************************ Internal functions ************************

def deletePlayLIstforUsr(req, key, token):
	url = misc.GetLoopBack() + '/playlists/' + key
	try:
		#TODO Change to native framework call, when Plex allows token in header
		opener = urllib2.build_opener(urllib2.HTTPHandler)
		request = urllib2.Request(url)
		request.add_header('X-Plex-Token', token)
		request.get_method = lambda: 'DELETE'
		url = opener.open(request)
	except Ex.HTTPError, e:
		Log.Exception('HTTP exception  when deleting a playlist for the owner was: %s' %(e))
		req.clear()
		req.set_status(e.code)			
		req.finish(str(e))
	except Exception, e:
		Log.Exception('Exception happened when deleting a playlist for the user was: %s' %(str(e)))
		req.clear()
		req.set_status(500)			
		req.finish('Exception happened when deleting a playlist for the user was: %s' %(str(e)))
	return req

#******************* Internal functions ***************************

# This function returns true or false, if key/path matches for a media
def checkItemIsValid(key, title, sType):
	url = misc.GetLoopBack() + '/library/metadata/' + str(key) + '?' + EXCLUDE	
	#TODO: Fix for other types
	print 'GED TODO Here'
	if sType == 'video':
		mediaTitle = XML.ElementFromURL(url).xpath('//Video')[0].get('title')		
	
	return (title == mediaTitle)
	
# This function will search for a a media based on title and type, and return the key
def searchForItemKey(title, sType):
	url = misc.GetLoopBack() + '/search?query=' + String.Quote(title) + '&' + EXCLUDE		
	try:
		result = []
		found = XML.ElementFromURL(url)
		#TODO: Fix for other types
		# Are we talking about a video here?
		if sType == 'video':				
			itemType = found.xpath('//Video/@type')[0]
			if itemType in ['movie', 'episode', 'show']:				
				ratingKey = found.xpath('//Video/@ratingKey')[0]
				result.append(ratingKey)
				librarySectionUUID = found.xpath('//Video/@librarySectionUUID')[0]
				result.append(librarySectionUUID)
				Log.Info('Item named %s was located as item with key %s' %(title, ratingKey))
				return result
	except Exception, e:		
		pass

