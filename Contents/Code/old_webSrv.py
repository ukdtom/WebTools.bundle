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

from tornado.web import RequestHandler, StaticFileHandler, Application
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
import threading


''' url /test helps devs to check that we are running '''
class testHandler(RequestHandler):
	def get(self):
		Log.Debug('Tornado recieved a test call')
		self.write("Hello, world, I'm alive")

		
# The default handler is the test handler
handlers = [(r'/test', testHandler)]

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
	# Path to http directory in the bundle, that we need to serve
	actualPath =  {'path': os.path.join(Core.app_support_path, 'Plug-ins', NAME + '.bundle', 'http')}
	rootpath = (r'/(.*)', StaticFileHandler, actualPath)
	global handlers
	handlers.append(rootpath)
	Log.Debug('tornado is handling the following URI: %s' %(handlers))
	t = threading.Thread(target=start_tornado)
	t.start()

