######################################################################################################################
#					WebTools helper unit
#
#					Runs a seperate webserver on a specified port
#					Author:			dane22, a Plex Community member
#
######################################################################################################################

import sys
# Add modules dir to search path
modules = Core.storage.join_path(Core.app_support_path, Core.config.bundles_dir_name, NAME + '.bundle', 'Contents', 'Code', 'modules')
sys.path.append(modules)

from tornado.web import *
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.escape import json_encode, xhtml_escape

import threading

# Migrated to new way
from plextvhelper import plexTV
from git import git
from logs import logs
from pms import pms
from settings import settings
from findMedia import findMedia
from language import language
from plex2csv import plex2csv
from wt import wt


import os

# Below used to find path of this file
from inspect import getsourcefile
from os.path import abspath


# TODO 
#from importlib import import_module
# SNIFF....Tornado is V1.0.0, meaning no WebSocket :-(

# Path to http folder within the bundle
def getActualHTTPPath():
	HTTPPath = Core.storage.join_path(Core.app_support_path, Core.config.bundles_dir_name, NAME + '.bundle', 'http')
	if not os.path.isdir(HTTPPath):
		Log.Critical('Could not find my http path in: ' + HTTPPath)
		return ''
	else:
		return HTTPPath

# Path to http folder within the bundle
def isCorrectPath(req):	
	installedPlugInPath, skipStr = abspath(getsourcefile(lambda:0)).upper().split('WEBTOOLS.BUNDLE',1)
	targetPath = Core.storage.join_path(Core.app_support_path, Core.config.bundles_dir_name).upper()
	if installedPlugInPath[:-1] != targetPath:
		installedPlugInPath, skipStr = abspath(getsourcefile(lambda:0)).split('/Contents',1)
		msg = '<h1>Wrong installation path detected</h1>'
		msg = msg + '<p>It seems like you installed WebTools into the wrong folder</p>'
		msg = msg + '<p>You installed WebTools here:<p>'
		msg = msg + installedPlugInPath
		msg = msg + '<p>but the correct folder is:<p>'
		msg = msg + Core.storage.join_path(Core.app_support_path, Core.config.bundles_dir_name, 'WebTools.bundle')
		req.clear()
		req.set_status(404)
		req.finish(msg)
	else:
		Log.Info('Verified a correct install path as: ' + targetPath)

#************** webTools functions ******************************
''' Here we have the supported functions '''
class webTools(object):
	# Defaults used by the rest of the class
	def __init__(self):
		# Not used yet
		return


	''' Return version number, and other info '''
	def getVersion(self):
		retVal = {'version': VERSION, 
						'PasswordSet': Dict['pwdset'],
						'PlexTVOnline': plexTV().auth2myPlex()}
		Log.Info('Version requested, returning ' + str(retVal))
		return retVal

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
		Log.Info('Returning: ' + Core.storage.join_path(getActualHTTPPath(), 'index.html'))
		self.render(Core.storage.join_path(getActualHTTPPath(), 'index.html'))

''' Logout handler '''
class LogoutHandler(BaseHandler):
	@authenticated
	def get(self):
		Log.Info('Clearing Auth Cookie')
		self.clear_cookie(NAME)
		self.redirect('/')

class LoginHandler(BaseHandler):
	def get(self):
		isCorrectPath(self)
		Log.Info('Returning login page: ' + Core.storage.join_path(getActualHTTPPath() , 'login.html'))
		self.render(Core.storage.join_path(getActualHTTPPath(), 'login.html'), next=self.get_argument("next","/"))

	def post(self):
		global AUTHTOKEN

		# Check for an auth header, in case a frontend wanted to use that
		# Header has precedence compared to params
		auth_header = self.request.headers.get('Authorization', None)
		if auth_header is None or not auth_header.startswith('Basic '):
			Log.Info('No Basic Auth header, so looking for params')
			user = self.get_argument('user', '')
			if user == '':
				if plexTV().auth2myPlex():
					Log.Info('Missing username')
					self.clear()
					self.set_status(412)
					self.finish("<html><body>Missing username</body></html>")
			pwd = self.get_argument('pwd', '')
			if pwd == '':
				Log.Info('Missing password')
				self.clear()
				self.set_status(412)
				self.finish("<html><body>Missing password</body></html>")
		else:
			Log.Info('Auth header found')
			auth_decoded = String.Base64Decode(auth_header[6:])
			user, pwd = auth_decoded.split(':', 2)
		Log.Info('User is: ' + user)
		# Allow no password when in debug mode
		if DEBUGMODE:
			self.allow()
			Log.Info('All is good, we are authenticated')
			self.redirect('/')
		# Let's start by checking if the server is online
		if plexTV().auth2myPlex():
			token = ''
			try:
				# Authenticate
				retVal = plexTV().isServerOwner(plexTV().login(user, pwd))
				self.clear()
				if retVal == 0:
					# All is good
					self.allow()
					Log.Info('All is good, we are authenticated')
					self.redirect('/')
				elif retVal == 1:
					# Server not found
					Log.Info('Server not found on plex.tv')
					self.set_status(404)
				elif retVal == 2:
					# Not the owner
					Log.Info('USer is not the server owner')
					self.set_status(403)
				else:
					# Unknown error
					Log.Critical('Unknown error, when authenticating')
					self.set_status(403)
			except Ex.HTTPError, e:
				Log.Critical('Exception in Login: ' + str(e))
				self.clear()
				self.set_status(e.code)
				self.finish(e)
				return self
		else:
			Log.Info('Server is not online according to plex.tv')
			# Server is offline
			if Dict['password'] == '':
				Log.Info('First local login, so we need to set the local password')
				Dict['password'] = pwd
				Dict['pwdset'] = True
				Dict.Save
				self.allow()
				self.redirect('/')
			elif Dict['password'] == pwd:
				self.allow()
				Log.Info('Local password accepted')
				self.redirect('/')
			elif Dict['password'] != pwd:
				Log.Critical('Either local login failed, or PMS lost connection to plex.tv')
				self.clear()
				self.set_status(401)

	def allow(self):
		self.set_secure_cookie(NAME, Hash.MD5(Dict['SharedSecret']+Dict['password']), expires_days = None)

class versionHandler(RequestHandler):
	def get(self, **params):
		self.set_header('Content-Type', 'application/json; charset=utf-8')
		self.write(webTools().getVersion())

class webTools2Handler(BaseHandler):
	# Disable auth when debug
	def prepare(self):
		if DEBUGMODE:
			self.set_secure_cookie(NAME, Hash.MD5(Dict['SharedSecret']+Dict['password']), expires_days = None)

	#******* GET REQUEST *********
	@authenticated
	# Get Request
	def get(self, **params):		
		module = self.get_argument('module', 'missing')
		if module == 'missing':
			self.clear()
			self.set_status(404)
			self.finish('Missing function call')
			return
		else:
			Log.Debug('Recieved a get call for module: ' + module)
	
#TODO
			''' Attempt to create a dynamic import, but so far, it sadly breaks access to the PMS API :-(
			import sys
			sys.path.append(os.path.join(Core.app_support_path, 'Plug-ins', NAME + '.bundle', 'Contents', 'Code'))
			mod = import_module(module)
			modClass = getattr(mod, module)()
			print 'GED1', dir(modClass)
			callFunction = getattr(modClass, 'reqprocess')
			self = modClass().reqprocess(self)
			'''

			if module == 'git':			
				self = git().reqprocess(self)
			elif module == 'logs':
				self = logs().reqprocess(self)
			elif module == 'pms':
				self = pms().reqprocess(self)
			elif module == 'settings':
				self = settings().reqprocess(self)
			elif module == 'findMedia':
				self = findMedia().reqprocess(self)
			elif module == 'language':
				self = language().reqprocess(self)
			elif module == 'plex2csv':
				self = plex2csv().reqprocess(self)
			elif module == 'wt':
				self = wt().reqprocess(self)
			else:
				self.clear()
				self.set_status(412)
				self.finish('Unknown module call')
				return



	#******* POST REQUEST *********
	@authenticated
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
			elif module == 'settings':			
				self = settings().reqprocessPost(self)
			elif module == 'pms':			
				self = pms().reqprocessPost(self)
			elif module == 'findMedia':		
				self = findMedia().reqprocessPost(self)
			elif module == 'wt':		
				self = wt().reqprocessPost(self)
			else:
				self.clear()
				self.set_status(412)
				self.finish('Unknown module call')
				return

	#******* DELETE REQUEST *********
	@authenticated
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
	def put(self, **params):
		module = self.get_argument('module', 'missing')
		if module == 'missing':
			self.clear()
			self.set_status(404)
			self.finish("<html><body>Missing function call</body></html>")
			return
		else:
			Log.Debug('Recieved a PUT call for module: ' + module)
			if module == 'settings':			
				self = settings().reqprocessPUT(self)
			elif module == 'git':			
				self = git().reqprocessPUT(self)
			elif module == 'pms':			
				self = pms().reqprocessPUT(self)
			else:
				self.clear()
				self.set_status(412)
				self.finish("<html><body>Unknown module call</body></html>")
				return

handlers = [(r"/login", LoginHandler),
						(r"/logout", LogoutHandler),
						(r"/version", versionHandler),
						(r'/', idxHandler),
						(r'/index.html', idxHandler),
						(r"/webtools2*$", webTools2Handler),
						(r'/(.*)', StaticFileHandler, {'path': getActualHTTPPath()})
]

if Prefs['Force_SSL']:
	httpHandlers = [(r"/login", ForceTSLHandler),
									(r"/logout", LogoutHandler),
									(r"/version", ForceTSLHandler),
									(r'/', ForceTSLHandler),
									(r'/index.html', ForceTSLHandler),
									(r"/webtools2*$", webTools2Handler)
]
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
def startWeb(secretKey, version, debugmode):
	global SECRETKEY	
	# Set the secret key for use by other calls in the future maybe?
	SECRETKEY = secretKey
	global VERSION
	VERSION = version
	global DEBUGMODE
	DEBUGMODE = debugmode
	stopWeb()
	Log.Debug('tornado is handling the following URI: %s' %(handlers))
	t = threading.Thread(target=start_tornado)
	t.start()

