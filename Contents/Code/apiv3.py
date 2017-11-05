'''
##############################################################################################
#	WebTools module unit
#
#	Author: dane22, a Plex Community member
#
# 	Handles calles to the API V3
#
##############################################################################################
'''

from tornado.web import *
from consts import DEBUGMODE, WT_AUTH, VERSION, NAME, V3MODULES
import sys

import wtV3
import pmsV3
import logsV3
import languageV3
import settingsV3
import gitV3
import findMediaV3
import jsonExporterV3
import playlistsV3
import techinfo
import viewstate

class BaseHandler(RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie(NAME)

# API V3


class apiv3(BaseHandler):
    module = None
    function = None

    # Disable auth when debug, and get module
    def prepare(self):
        # Set Default header
        self.set_header('Cache-Control',
                        'no-store, no-cache, must-revalidate, max-age=0')
        # Get the module
        params = self.request.uri[8:].upper().split('/')
        for param in params:
            if param in V3MODULES:
                self.module = param
            else:
                self.function = param
        # Check if we should bypass auth
        if DEBUGMODE:
            if not WT_AUTH:
                self.set_secure_cookie(NAME, Hash.MD5(
                    Dict['SharedSecret'] + Dict['password']), expires_days=None)
        # No valid module found?
        if not self.module:
            self.clear()
            self.set_status(404)
            self.finish('Missing module or unknown module')

    # Make the call
    # TODO: Make this more dynamic if possible
    def makeCall(self):
        Log.Debug('Recieved an apiV3 call for module: ' +
                  self.module + ' for method: ' + self.request.method)
        # Generate a handle to the class
        try:
            myClass = getattr(pmsV3, V3MODULES[self.module])
        except:
            try:
                myClass = getattr(wtV3, V3MODULES[self.module])
            except:
                try:
                    myClass = getattr(logsV3, V3MODULES[self.module])
                except:
                    try:
                        myClass = getattr(languageV3, V3MODULES[self.module])
                    except:
                        try:
                            myClass = getattr(
                                settingsV3, V3MODULES[self.module])
                        except:
                            try:
                                myClass = getattr(
                                    gitV3, V3MODULES[self.module])
                            except:
                                try:
                                    myClass = getattr(
                                        findMediaV3, V3MODULES[self.module])
                                except:
                                    try:
                                        myClass = getattr(
                                            jsonExporterV3, V3MODULES[self.module])
                                    except:
                                        try:
                                            myClass = getattr(
                                                playlistsV3, V3MODULES[self.module])
                                        except:
                                            try:
                                                myClass = getattr(
                                                    techinfo, V3MODULES[self.module])
                                            except:
                                                try:
                                                    myClass = getattr(
                                                        viewstate, V3MODULES[self.module])                                                    
                                                except Exception, e:
                                                    Log.Exception(
                                                        'Exception getting the class in apiV3: %s' % str(e))
                                                    self.clear()
                                                    self.set_status(501)
                                                    self.finish('Bad module?')
        try:
            # Make the call
            getattr(myClass, 'getFunction')(self.request.method.lower(), self)
        except Exception, e:
            Log.Exception('Exception apiV3 call reqprocess: ' + str(e))
            self.clear()
            self.set_status(501)
            self.finish('Bad reqprocess call?')

    '''******* GET REQUEST *********'''
    @authenticated
    def get(self, **params):
        self.makeCall()

    '''******* POST REQUEST *********'''
    @authenticated
    def post(self, **params):
        self.makeCall()

    '''******* PUT REQUEST *********'''
    @authenticated
    def put(self, **params):
        self.makeCall()

    '''******* DELETE REQUEST *********'''
    @authenticated
    def delete(self, **params):
        self.makeCall()
