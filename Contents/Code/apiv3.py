######################################################################################################################
#	WebTools module unit					
#
#	Author: dane22, a Plex Community member
#
# Handles calles to the API V3
#
######################################################################################################################

from tornado.web import *
from consts import DEBUGMODE, WT_AUTH, VERSION, NAME, MODULES

# Import modules
from wtV3 import wtV3

class BaseHandler(RequestHandler):	
	def get_current_user(self):
		return self.get_secure_cookie(NAME)

# API V3
class apiv3(BaseHandler):	

	module = None

	# Disable auth when debug
	def prepare(self):
		# Set Default header
		self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
		# Got a valid module call
		self.validModules()
		# Check if we should bypass auth
		if DEBUGMODE:
			if not WT_AUTH:
				self.set_secure_cookie(NAME, Hash.MD5(Dict['SharedSecret']+Dict['password']), expires_days = None)

	# Check if a valid module was requested
	def validModules(self):
		module = self.get_argument('module', 'missing')
		if module.upper() not in MODULES:
			self.clear()
			self.set_status(404)
			self.finish('Missing module or unknown module')
			self.module = None
		else:
			self.module = module

	#******* GET REQUEST *********
	@authenticated
	# Get Request
	def get(self, **params):
		Log.Debug('Recieved a GET call for module: ' + self.module)
		try:
			if self.module == 'wt':
				self = wtV3().reqprocessGET(self)
			else:
				self.clear()
				self.set_status(501)
				self.finish('Not implemented')
				self.module = None
		except Exception, e:
			Log.Debug('Exception in apiV3: ' + str(e))
			self.clear()
			self.set_status(500)
			self.finish('Fatal error: %s' %(str(e)))
			self.module = None

	#******* POST REQUEST *********
	@authenticated
	def post(self, **params):
		Log.Debug('Recieved a POST call for module: ' + module)
		try:
			if self.module == 'wt':
				self = wtV3().reqprocessPOST(self)
			else:
				self.clear()
				self.set_status(501)
				self.finish('Not implemented')
				self.module = None
		except Exception, e:
			Log.Debug('Exception in apiV3: ' + str(e))
			self.clear()
			self.set_status(500)
			self.finish('Fatal error: %s' %(str(e)))
			self.module = None

	#******* PUT REQUEST *********
	@authenticated
	def put(self, **params):
		Log.Debug('Recieved a PUT call for module: ' + self.module)
		try:
			if self.module == 'wt':
				self = wtV3().reqprocessPUT(self)
			else:
				self.clear()
				self.set_status(501)
				self.finish('Not implemented')
				self.module = None
		except Exception, e:
			Log.Debug('Exception in apiV3: ' + str(e))
			self.clear()
			self.set_status(500)
			self.finish('Fatal error: %s' %(str(e)))
			self.module = None








