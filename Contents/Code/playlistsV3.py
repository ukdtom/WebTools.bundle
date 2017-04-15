######################################################################################################################
#	Playlist module unit					
#
#	Author: dane22, a Plex Community member
#
# A WebTools module for handling playlists
#
######################################################################################################################
import time
import json
from misc import misc
from plextvhelper import plexTV
#TODO: Remove when Plex framework allows token in the header
import urllib2
from xml.etree import ElementTree
#TODO End


GET = ['LIST', 'DOWNLOAD']
PUT = []
POST = []
DELETE = []

class playlistsV3(object):
	# Defaults used by the rest of the class
	@classmethod
	def init(self):
		self.getListsURL = misc.GetLoopBack() + '/playlists/all'	

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
					else:
						Log.Info('Invalid params for playlists.list ignored')
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
#				playlists = XML.ElementFromURL(self.getListsURL, headers=myHeader)
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

