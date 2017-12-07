######################################################################################################################
#					WebTools helper unit
#
#					Runs a seperate webserver on a specified port
#					Author:			dane22, a Plex Community member
#
######################################################################################################################

from consts import DEBUGMODE, WT_AUTH, VERSION, NAME, V3MODULES, BASEURL, UILANGUAGE, UILANGUAGEDEBUG, WT_URL


import sys
# Add modules dir to search path
modules = Core.storage.join_path(
    Core.app_support_path, Core.config.bundles_dir_name, NAME + '.bundle', 'Contents', 'Code', 'modules')
sys.path.append(modules)

from tornado.web import *
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.escape import json_encode, xhtml_escape


import threading
import os
import sys
import time

import apiv3
from plextvhelper import plexTV
from wtV3 import wtV3

# Below used to find path of this file
from inspect import getsourcefile
from os.path import abspath


# TODO
# from importlib import import_module
# SNIFF....Tornado is V1.0.0, meaning no WebSocket :-(

# Path to http folder within the bundle
def getActualHTTPPath():
    try:
        HTTPPath = os.path.normpath(
            Core.storage.join_path(Core.bundle_path, 'http'))
        if not os.path.isdir(HTTPPath):
            Log.Critical('Could not find my http path in: ' + HTTPPath)
            return ''
        else:
            return HTTPPath
    except Exception, e:
        Log.Exception('Exception in getActualHTTPPath was %s' % (str(e)))

# Path to bundle folder within the bundle


def isCorrectPath(req):
    try:
        installedPlugInPath = os.path.normpath(
            abspath(getsourcefile(lambda: 0)).split(str(NAME) + '.bundle', 1)[0])
        targetPath = os.path.normpath(Core.storage.join_path(
            Core.app_support_path, Core.config.bundles_dir_name))
        if installedPlugInPath != targetPath:
            Log.Debug('************************************************')
            Log.Debug('Wrong installation path detected!!!!')
            Log.Debug('')
            Log.Debug('Currently installed in:')
            Log.Debug(installedPlugInPath)
            Log.Debug('Correct path is:')
            Log.Debug(Core.storage.join_path(Core.app_support_path,
                                             Core.config.bundles_dir_name, NAME + '.bundle'))
            Log.Debug('************************************************')
            installedPlugInPath, skipStr = abspath(
                getsourcefile(lambda: 0)).split('/Contents', 1)
            msg = '<h1>Wrong installation path detected</h1>'
            msg = msg + '<p>It seems like you installed ' + \
                NAME + ' into the wrong folder</p>'
            msg = msg + '<p>You installed ' + NAME + ' here:<p>'
            msg = msg + installedPlugInPath
            msg = msg + '<p>but the correct folder is:<p>'
            msg = msg + Core.storage.join_path(
                Core.app_support_path, Core.config.bundles_dir_name, NAME + '.bundle')
            req.clear()
            req.set_status(404)
            req.finish(msg)
        else:
            Log.Info('Verified a correct install path as: ' + targetPath)
    except Exception, e:
        Log.Exception('Exception in isCorrectPath was %s' % (str(e)))


#************** webTools functions ******************************
''' Here we have the supported functions '''


class webTools(object):
    # Defaults used by the rest of the class
    def __init__(self):
        # Not used yet
        return

        ''' Return version number, and other info '''

    def getVersion(self):
        try:
            scheme = Dict['wt_csstheme']
            if scheme == None:
                scheme = ''
            retVal = {'version': VERSION, 'PasswordSet': Dict['pwdset'], 'PlexTVOnline': plexTV().auth2myPlex(
            ), 'wt_csstheme': scheme, 'UILanguageDebug': UILANGUAGEDEBUG, 'UILanguage': Dict['UILanguage'], 'WT_URL': WT_URL}
            Log.Info('Version requested, returning ' + str(retVal))
            return retVal
        except Exception, e:
            Log.Exception('Exception in getVersion: %s' % (str(e)))

#**************** Handler Classes for Rest **********************


class MyStaticFileHandler(StaticFileHandler):
    def set_extra_headers(self, path):
        # Disable cache
        self.set_header('Cache-Control',
                        'no-store, no-cache, must-revalidate, max-age=0')


class BaseHandler(RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie(NAME)


''' handler to force TLS '''


class ForceTSLHandler(RequestHandler):
    def get(self):
        ''' This is sadly up hill, due to the old version of Tornado used :-( '''
        # Grap the host requested
        host, port = self.request.headers['Host'].split(':')
        newUrl = 'https://' + host + ':' + \
            Prefs['WEB_Port_https'] + BASEURL + '/login'
        self.redirect(newUrl, permanent=True)


''' If user didn't enter the full path '''


class idxHandler(BaseHandler):
    @authenticated
    def get(self):
        # If hitting root, but without an ending slash, redirect to that
        if self.request.uri == BASEURL:
            self.redirect('%s/' % BASEURL)
        Log.Info('Returning: ' +
                 Core.storage.join_path(getActualHTTPPath(), 'index.html'))
        self.set_header('Cache-Control',
                        'no-store, no-cache, must-revalidate, max-age=0')
        self.render(Core.storage.join_path(getActualHTTPPath(), 'index.html'))


''' Logout handler '''


class LogoutHandler(BaseHandler):
    @authenticated
    def get(self):
        Log.Info('Clearing Auth Cookie')
        self.clear_cookie(NAME)
        self.redirect('%s/' % BASEURL)


class LoginHandler(BaseHandler):
    def get(self):
        isCorrectPath(self)
        Log.Info('Returning login page: ' +
                 Core.storage.join_path(getActualHTTPPath(), 'login.html'))
        self.render(Core.storage.join_path(getActualHTTPPath(),
                                           'login.html'), next=self.get_argument("next", "/"))

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
                    self.finish('Missing username')
            pwd = self.get_argument('pwd', '')
            if pwd == '':
                Log.Info('Missing password')
                self.clear()
                self.set_status(412)
                self.finish('Missing password')
        else:
            Log.Info('Auth header found')
            auth_decoded = String.Base64Decode(auth_header[6:])
            user, pwd = auth_decoded.split(':', 2)
        Log.Info('User is: ' + user)
        # Allow no password when in debug mode
        if DEBUGMODE:
            if not WT_AUTH:
                self.allow()
                Log.Info('All is good, we are authenticated')
                self.redirect('%s/' % BASEURL)
            else:
                # Let's start by checking if the server is online
                if plexTV().auth2myPlex():
                    token = ''
                    try:
                        # Authenticate
                        login_token = plexTV().login(user, pwd)
                        if login_token == None:
                            Log.Error(
                                'Bad credentials detected, denying access')
                            self.clear()
                            self.set_status(401)
                            self.finish('Authentication error')
                            return self
                        retVal = plexTV().isServerOwner(login_token)
                        self.clear()
                        if retVal == 0:
                            # All is good
                            self.allow()
                            Log.Info('All is good, we are authenticated')
                            self.redirect('%s/' % BASEURL)
                        elif retVal == 1:
                            # Server not found
                            Log.Info('Server not found on plex.tv')
                            self.set_status(404)
                        elif retVal == 2:
                            # Not the owner
                            Log.Info('User is not the server owner')
                            self.set_status(403)
                        else:
                            # Unknown error
                            Log.Critical('Unknown error, when authenticating')
                            self.set_status(403)
                    except Ex.HTTPError, e:
                        Log.Exception('Exception in Login: ' + str(e))
                        self.clear()
                        self.set_status(e.code)
                        self.finish(str(e))
                        return self
                    except Exception, e:
                        Log.Exception('Exception in Login: ' + str(e))
                        self.clear()
                        self.set_status(e.code)
                        self.finish(str(e))
                        return self
        else:
            # Let's start by checking if the server is online
            try:
                if plexTV().auth2myPlex():
                    token = ''
                    try:
                        # Authenticate
                        login_token = plexTV().login(user, pwd)
                        if login_token == None:
                            Log.Error(
                                'Bad credentials detected, denying access')
                            self.clear()
                            self.set_status(401)
                            self.finish('Authentication error')
                            return self
                        retVal = plexTV().isServerOwner(login_token)
                        self.clear()
                        if retVal == 0:
                            # All is good
                            self.allow()
                            Log.Info('All is good, we are authenticated')
                            self.redirect('%s/' % BASEURL)
                        elif retVal == 1:
                            # Server not found
                            Log.Info('Server not found on plex.tv')
                            self.set_status(404)
                        elif retVal == 2:
                            # Not the owner
                            Log.Info('User is not the server owner')
                            self.set_status(403)
                        else:
                            # Unknown error
                            Log.Critical('Unknown error, when authenticating')
                            self.set_status(403)
                    except Ex.HTTPError, e:
                        Log.Exception('Exception in Login: ' + str(e))
                        self.clear()
                        self.set_status(e.code)
                        self.finish(str(e))
                        return self
                    except Exception, e:
                        Log.Exception('Exception in Login: ' + str(e))
                        self.clear()
                        self.set_status(e.code)
                        self.finish(str(e))
                        return self
            except Exception, e:
                Log.Exception('Exception in Login: ' + str(e))
                self.clear()
                self.set_status(e.code)
                self.finish(str(e))
                return self
            else:
                Log.Info('Server is not online according to plex.tv')
                # Server is offline
                if Dict['password'] == '':
                    Log.Info(
                        'First local login, so we need to set the local password')
                    Dict['password'] = pwd
                    Dict['pwdset'] = True
                    Dict.Save
                    self.allow()
                    self.redirect('%s/' % BASEURL)
                elif Dict['password'] == pwd:
                    self.allow()
                    Log.Info('Local password accepted')
                    self.redirect('%s/' % BASEURL)
                elif Dict['password'] != pwd:
                    Log.Critical(
                        'Either local login failed, or PMS lost connection to plex.tv')
                    self.clear()
                    self.set_status(401)

    def allow(self):
        self.set_secure_cookie(NAME, Hash.MD5(
            Dict['SharedSecret'] + Dict['password']), expires_days=None)


class versionHandler(RequestHandler):
    def get(self, **params):
        self.set_header('Content-Type', 'application/json; charset=utf-8')
        self.set_header('Cache-Control',
                        'no-store, no-cache, must-revalidate, max-age=0')
        self.write(webTools().getVersion())


''' Handler to get images from the DATA API '''


class imageHandler(RequestHandler):
    def get(self, **params):
        # Get name of image
        trash, image = self.request.uri.rsplit('/', 1)
        if Data.Exists(image):
            # Get file extention
            trash, extension = os.path.splitext(image)
            # Set content-type in header
            contenttype = 'image/' + extension[1:]
            self.set_header('Cache-Control',
                            'no-store, no-cache, must-revalidate, max-age=0')
            self.set_header('Content-Type',  contenttype)
            try:
                # Redirect to unknown icon, in case frontend dev forgets ;-)
                if image == '':
                    image = 'NoIcon.png'
                self.write(Data.Load(image))
                self.finish()
            except Exception, e:
                Log.Exception('Exception in imageHandler was: %s' % (str(e)))
        else:
            self.set_status(404)
            self.finish()


class translateHandler(RequestHandler):
    def get(self, **params):
        # Name of javascript
        fileName = 'translations.js'
        if Data.Exists(fileName):
            # Set content-type in header
            contenttype = 'application/javascript'
            self.set_header('Cache-Control',
                            'no-store, no-cache, must-revalidate, max-age=0')
            self.set_header('Content-Type',  contenttype)
            try:
                self.write(Data.Load(fileName))
                self.finish()
            except Exception, e:
                Log.Exception(
                    'Exception in translateHandler was: %s' % (str(e)))
        else:
            Log.Critical('Could not find translations.js')
            self.set_status(404)
            self.write('Missing translation script')
            self.finish()


''' getTranslationHandler '''


class getTranslationHandler(RequestHandler):
    def post(self, **params):
        self.set_header('Content-Type', 'application/json; charset=utf-8')
        self.set_header('Cache-Control',
                        'no-store, no-cache, must-revalidate, max-age=0')
        self.write(wtV3().GETTRANSLATE(self, **params))


''' handlers '''
handlers = [(r"%s/login" % BASEURL, LoginHandler),
            (r"%s/logout" % BASEURL, LogoutHandler),
            (r"%s/version" % BASEURL, versionHandler),
            # Grap images from Data framework
            (r"%s/uas/Resources.*$" % BASEURL, imageHandler),
            # Grap translation.js from datastore
            (r"%s/static/_shared/translations.js" % BASEURL, translateHandler),
            (r'%s/' % BASEURL, idxHandler),																# Index
            (r'%s' % BASEURL, idxHandler),																# Index
            (r'%s/index.html' % BASEURL, idxHandler),													# Index
            (r'%s/api/v3.*$' % BASEURL, apiv3.apiv3),													# API V3
            (r'%s/getTranslate.*$' %
             BASEURL, getTranslationHandler),													        # getTranslation
            (r'%s/(.*)' % BASEURL, MyStaticFileHandler,
             {'path': getActualHTTPPath()})					# Static files
            ]

if Prefs['Force_SSL']:
    httpHandlers = [(r"%s/login" % BASEURL, ForceTSLHandler),
                    (r"%s/logout" % BASEURL, LogoutHandler),
                    (r"%s/version" % BASEURL, ForceTSLHandler),
                    (r'%s/' % BASEURL, ForceTSLHandler),
                    (r'%s/index.html' % BASEURL, ForceTSLHandler),
                    # Grap images from Data framework
                    (r"%s/uas/Resources.*$" % BASEURL, imageHandler),
                    (r'%s/getTranslate.*$' %
                     BASEURL, getTranslationHandler),													 # getTranslation
                    # Grap translation.js from datastore
                    (r"%s/static/_shared/translations.js" %
                     BASEURL, translateHandler),
                    (r'%s/api/v3.*$' % BASEURL, apiv3.apiv3)
                    ]
else:
    httpHandlers = handlers

httpsHandlers = handlers

#********* Tornado itself *******************

''' Start the actual instance of tornado '''


def start_tornado():
    myCookie = Hash.MD5(Dict['SharedSecret'] + NAME)
    login_url = BASEURL + '/login'
    settings = {"cookie_secret": "__" + myCookie + "__",
                "login_url": login_url}
    try:
        application = Application(httpHandlers, **settings)
        applicationTLS = Application(httpsHandlers, **settings)
        http_server = HTTPServer(application)
        # Use our own certificate for TLS
        CRTFile = os.path.join(Core.bundle_path, 'Contents',
                               'Code', 'Certificate', Prefs['Cert_CRT'])
        Log.Info('Certificate crt file is %s' % CRTFile)
        KEYFile = os.path.join(Core.bundle_path, 'Contents',
                               'Code', 'Certificate', Prefs['Cert_KEY'])
        Log.Info('Certificate key file is %s' % KEYFile)
        http_serverTLS = HTTPServer(applicationTLS,
                                    ssl_options={
                                        "certfile": os.path.join(Core.bundle_path, 'Contents', 'Code', 'Certificate', CRTFile),
                                        "keyfile": KEYFile})
        # Set web server port to the setting in the channel prefs
        port = int(Prefs['WEB_Port_http'])
        ports = int(Prefs['WEB_Port_https'])
        http_server.listen(port)
        http_serverTLS.listen(ports)
        Log.Debug('Starting tornado on ports %s and %s' % (port, ports))
        IOLoop.instance().start()
    except Exception, e:
        Log.Exception('Problem starting Tornado: ' + str(e))


''' Stop the actual instance of tornado '''


def stopWeb():
    IOLoop.instance().add_callback(IOLoop.instance().stop)
    Log.Debug('Asked Tornado to exit')


''' Main call '''
# def startWeb(secretKey, version):


def startWeb(secretKey):
    global SECRETKEY
    # Set the secret key for use by other calls in the future maybe?
    SECRETKEY = secretKey
    stopWeb()
    time.sleep(3)
    Log.Debug('tornado is handling the following URI: %s' % (handlers))
    t = threading.Thread(target=start_tornado)
    t.start()
