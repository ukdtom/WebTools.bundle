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
		self.resourceURL = self.mainUrl + '/pms/resources.xml'
		# Mandentory headers
		self.myHeader = {}
		self.myHeader['X-Plex-Client-Identifier'] = NAME + '-' + self.get_thisPMSIdentity()
		self.myHeader['Accept'] = 'application/xml'
		self.myHeader['X-Plex-Product'] = NAME
		self.myHeader['X-Plex-Device-Name'] = NAME + '-' + self.get_thisPMSIdentity()
		self.myHeader['X-Plex-Version'] = VERSION
		self.myHeader['X-Plex-Platform'] = Platform.OS

	# Login to Plex.tv
	def login(self, req):
		Log.Debug('Start to auth towards plex.tv')
		user = req.get_argument('user', '')
		if user == '':
			req.clear()
			req.set_status(412)
			req.finish("<html><body>Missing username</body></html>")
			return req
		pwd = req.get_argument('pwd', '')
		if pwd == '':
			req.clear()
			req.set_status(412)
			req.finish("<html><body>Missing password</body></html>")
			return req
		# Got what we needed, so let's logon
		authString = String.Base64Encode('%s:%s' % (user, pwd))
		self.myHeader['Authorization'] = 'Basic ' + authString
		try:
			token = XML.ElementFromURL(self.loginUrl, headers=self.myHeader, method='POST').xpath('//user')[0].get('authenticationToken')
			Log.Debug('Authenticated towards plex.tv with success')				
			return token
		except Ex.HTTPError, e:
			req.clear()
			req.set_status(e.code)
			req.finish(e)
			return (req, '')
		
	''' Is user the owner of the server?
			user identified by token
			server identified by clientIdentifier
			if server found, and user is the owner, return 0
			if server is not found, return 1
			if user is not the owner, return 2
			if unknow error, return -1
	'''
	def isServerOwner(self, token):
		Log.Debug('Checking server for ownership')
		try:
			# Ident of this server
			PMSId = XML.ElementFromURL('http://127.0.0.1:32400/identity').get('machineIdentifier')
			# Grap Resource list from plex.tv
			self.myHeader['X-Plex-Token'] = token
			elements = XML.ElementFromURL(self.resourceURL, headers=self.myHeader).xpath('//Device[@clientIdentifier="' + PMSId + '"]/@owned')
			if len(elements) < 1:
				Log.Debug('Server %s was not found @ plex.tv' %(PMSId))
				return 1
			else:
				if elements[0] == '1':
					Log.Debug('Authenticated ok towards %s' %(PMSId))
					return 0
				else:
					Log.Debug('Server %s was found @ plex.tv, but user is not the owner' %(PMSId))
					return 2
		except Ex.HTTPError, e:
			Log.Debug('Unknown exception was: %s' %(e))
			return -1

	''' will return the machineIdentity of this server '''
	def get_thisPMSIdentity(self):
		return XML.ElementFromURL('http://127.0.0.1:32400/identity').get('machineIdentifier')

	''' Will return true, if PMS is authenticated towards plex.tv '''
	def auth2myPlex(self):
		return 'ok' == XML.ElementFromURL('http://127.0.0.1:32400').get('myPlexSigninState')
	







