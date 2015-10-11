######################################################################################################################
#	Plex.tv helper unit					
#
#	Author: dane22, a Plex Community member
#
# NAME variable must be defined in the calling unit, and is the name of the application
#
######################################################################################################################

class plexTV(object):
	# Defaults used by the rest of the class
	def __init__(self):
		# Endpoints @ Plex server
		self.mainUrl = 'https://plex.tv'
		self.loginUrl = self.mainUrl + '/users/sign_in'
		self.serverUrl = self.mainUrl + '/pms/servers'
		# Mandentory headers
		self.myHeader = {}
		self.myHeader['X-Plex-Client-Identifier'] = NAME + '-' + self.get_thisPMSIdentity()
		self.myHeader['Accept'] = 'application/xml'
		self.myHeader['X-Plex-Product'] = NAME
		self.myHeader['X-Plex-Device-Name'] = NAME + '-' + self.get_thisPMSIdentity()
		self.myHeader['X-Plex-Version'] = VERSION
		self.myHeader['X-Plex-Platform'] = Platform.OS	

	''' Do a login against plex.tv, and return the token as a string. '''
	def login(self, user, pwd):
		authString = String.Base64Encode('%s:%s' % (user, pwd))
		self.myHeader['Authorization'] = 'Basic ' + authString
		try:
			response = HTTP.Request(self.loginUrl, headers=self.myHeader, method='POST')
			Token = XML.ObjectFromString(response.content).xpath('//user')[0].get('authenticationToken')		
			Log.Debug('Authenticated towards plex.tv with success')		
			return Token
		except:
			Log.Debug('Auth error in plex.tv')
			return 'Auth error in plex.tv'

	''' Will return a list of devices user has access to. '''
	def get_ServerList(self, token):
		self.myHeader['X-Plex-Token'] = token
		try:
			response = HTTP.Request(self.serverUrl, headers=self.myHeader)
			devices = XML.ObjectFromString(response.content).xpath('//Server')		
			Log.Debug('ServerList retrieved with success')
			return devices
		except:
			Log.Debug('Unknown error in plex.tv')
			return 'Unknown error in plex.tv'

	''' if user identified by token is the owner of the server, then returns true, else false '''
	def isServerOwner(self, machineIdentifier, token):
		Log.Debug('Checking server %s for ownership' %(machineIdentifier))
		servers =	self.get_ServerList(token)
		for server in servers:
			if server.get('machineIdentifier') == machineIdentifier:
				return server.get('owned')=='1'

	''' will return the machineIdentity of this server '''
	def get_thisPMSIdentity(self):
		return XML.ElementFromURL('http://127.0.0.1:32400/identity').get('machineIdentifier')

	''' Will return true, if PMS is authenticated towards plex.tv '''
	def auth2myPlex(self):
		return 'ok' == XML.ElementFromURL('http://127.0.0.1:32400').get('myPlexSigninState')
	







