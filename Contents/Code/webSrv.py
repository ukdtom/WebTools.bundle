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
from findUnmatched import findUnmatched

# TODO 
#from importlib import import_module

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

''' Logout handler '''
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
			'''
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
			elif module == 'findUnmatched':
				self = findUnmatched().reqprocess(self)
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
			elif module == 'settings':			
				self = settings().reqprocessPost(self)
			elif module == 'pms':			
				self = pms().reqprocessPost(self)
			elif module == 'findUnmatched':		
				self = findUnmatched().reqprocessPost(self)
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
						(r'/(.*)', StaticFileHandler, {'path': ACTUALPATH})
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
def startWeb(secretKey):
	global SECRETKEY
	# Set the secret key for use by other calls in the future maybe?
	SECRETKEY = secretKey
	stopWeb()
	Log.Debug('tornado is handling the following URI: %s' %(handlers))
	t = threading.Thread(target=start_tornado)
	t.start()

