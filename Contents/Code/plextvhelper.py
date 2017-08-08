######################################################################################################################
#	Plex.tv helper unit					
#
#	Author: dane22, a Plex Community member
#
######################################################################################################################
import sys
from misc import misc

from consts import VERSION, PREFIX, NAME

token = None

class plexTV(object):
	# Defaults used by the rest of the class
	def __init__(self):
		# Endpoints @ Plex server
		self.mainUrl = 'https://plex.tv'
		self.id = self.get_thisPMSIdentity()
		self.loginUrl = self.mainUrl + '/users/sign_in'
		self.serverUrl = self.mainUrl + '/pms/servers'
		self.resourceURL = self.mainUrl + '/pms/resources.xml'
		self.userURL = self.mainUrl + '/api/users'
		self.sharedServersURL = self.mainUrl + '/api/servers/' + self.id + '/shared_servers'
		self.token = None
		# Mandentory headers
		self.myHeader = {}
		self.myHeader['X-Plex-Client-Identifier'] = NAME + '-' + self.id
		self.myHeader['Accept'] = 'application/json'
		self.myHeader['X-Plex-Product'] = NAME
		self.myHeader['X-Plex-Version'] = VERSION
		self.myHeader['X-Plex-Platform'] = Platform.OS

	# Login to Plex.tv
	def login(self, user, pwd):
		Log.Info('Start to auth towards plex.tv')
		authString = String.Base64Encode('%s:%s' % (user, pwd))
		self.myHeader['Authorization'] = 'Basic ' + authString
		try:
			global token
			token = JSON.ObjectFromURL(self.loginUrl + '.json', headers=self.myHeader, method='POST')['user']['authToken']
			Log.Info('Authenticated towards plex.tv with success')				
			return token
		except Ex.HTTPError, e:
			Log.Exception('Login error: %s' %(str(e)))
			return None
		except Exception, e:
			Log.Exception('Login error: %s' %(str(e)))
			return None
		
	''' Is user the owner of the server?
			user identified by token
			server identified by clientIdentifier
			if server found, and user is the owner, return 0
			if server is not found, return 1
			if user is not the owner, return 2
			if unknown error, return -1
	'''
	def isServerOwner(self, token):
		Log.Debug('Checking server for ownership')
		try:
			# Grap Resource list from plex.tv
			self.myHeader['X-Plex-Token'] = token
			elements = XML.ElementFromURL(self.resourceURL, headers=self.myHeader).xpath('//Device[@clientIdentifier="' + self.id + '"]/@owned')
			if len(elements) < 1:
				Log.Debug('Server %s was not found @ plex.tv' %(self.id))
				return 1
			else:
				if elements[0] == '1':
					Log.Debug('Authenticated ok towards %s' %(self.id))
					return 0
				else:
					Log.Debug('Server %s was found @ plex.tv, but user is not the owner' %(self.id))
					return 2
		except Ex.HTTPError, e:
			Log.Exception('Unknown exception was: %s' %(e))
			return -1

	''' will return the machineIdentity of this server '''
	def get_thisPMSIdentity(self):				
		return XML.ElementFromURL(misc.GetLoopBack() + '/identity').get('machineIdentifier')

	''' Will return true, if PMS is authenticated towards plex.tv '''
	def auth2myPlex(self):		
		return 'ok' == XML.ElementFromURL(misc.GetLoopBack()).get('myPlexSigninState')

	''' Get list of users 
	This will return a json of users on the server, incl. their access token
	'''
	def getUserList(self):
		try:
			# Fetch resources from plex.tv
			self.myHeader['X-Plex-Token'] = token
			users = XML.ElementFromURL(self.userURL, headers=self.myHeader)
			sharedUsers = XML.ElementFromURL(self.sharedServersURL, headers=self.myHeader)
			usrList = {}
			for user in users:
				# Get servers for user
				servers = user.xpath('//Server')
				for server in servers:
					if server.get('machineIdentifier') == self.id:
						if len(sharedUsers.xpath('//SharedServer[@userID=' + user.get('id') + ']/@accessToken')) > 0:
#							usr = user.get('title')
							usr = user.get('id')
							usrList[usr] = {}
							usrList[usr]['title'] = user.get('title')
							usrList[usr]['recommendationsPlaylistId'] = user.get('recommendationsPlaylistId')
							usrList[usr]['thumb'] = user.get('thumb')
							usrList[usr]['protected'] = user.get('protected')
							usrList[usr]['home'] = user.get('home')
							usrList[usr]['allowSync'] = user.get('allowSync')
							usrList[usr]['allowCameraUpload'] = user.get('allowCameraUpload')
							usrList[usr]['allowChannels'] = user.get('allowChannels')
							usrList[usr]['filterAll'] = user.get('filterAll')
							usrList[usr]['filterMovies'] = user.get('filterMovies')
							usrList[usr]['filterMusic'] = user.get('filterMusic')
							usrList[usr]['filterPhotos'] = user.get('filterPhotos')
							usrList[usr]['filterTelevision'] = user.get('filterTelevision')
							usrList[usr]['restricted'] = user.get('restricted')
							usrList[usr]['accessToken'] = sharedUsers.xpath('//SharedServer[@userID=' + user.get('id') + ']/@accessToken')[0]
							usrList[usr]['username'] = sharedUsers.xpath('//SharedServer[@userID=' + user.get('id') + ']/@username')[0]
							usrList[usr]['email'] = sharedUsers.xpath('//SharedServer[@userID=' + user.get('id') + ']/@email')[0]
							usrList[usr]['acceptedAt'] = sharedUsers.xpath('//SharedServer[@userID=' + user.get('id') + ']/@acceptedAt')[0]
							usrList[usr]['invitedAt'] = sharedUsers.xpath('//SharedServer[@userID=' + user.get('id') + ']/@invitedAt')[0]
							# Get shares for the user
							shares = sharedUsers.xpath('//SharedServer[@userID=' + user.get('id') + ']/Section')
							usrShared = {}
							for share in shares:
								usrShared[share.get('id')] = {}
								usrShared[share.get('id')]['key'] = share.get('key')
								usrShared[share.get('id')]['title'] = share.get('title')
								usrShared[share.get('id')]['type'] = share.get('type')
								usrShared[share.get('id')]['shared'] = share.get('shared')
							usrList[usr]['shared'] = usrShared
			return usrList
		except Exception, e:
			Log.Exception('Fatal error happened in getUserList ' + str(e))

