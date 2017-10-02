######################################################################################################################
#	Language helper unit
#
#	Author: dane22, a Plex Community member
#
# This unit works with supported languages within Plex
#
# NAME variable must be defined in the calling unit, and is the name of the application
#
######################################################################################################################

import json
import sys
from consts import ISO639_3

GET = ['GETLANGCODE3LIST', 'GET3CODELANGLIST', 'GETCODELANGLIST',
       'GETLANGCODELIST', 'GETLANGCODELIST', 'GETCOUNTRYCODES']
PUT = ['']
POST = ['GETMATCH']
DELETE = ['']


class languageV3(object):
    init_already = False

    @classmethod
    def init(self):
        return

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
            paramsStr = req.request.uri[req.request.uri.upper().find(
                self.function) + len(self.function):]
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
                Log.Debug('Function to call is: ' + self.function +
                          ' with params: ' + str(params))
                if params == None:
                    getattr(self, self.function)(req)
                else:
                    getattr(self, self.function)(req, params)
            except Exception, e:
                Log.Exception('Exception in process of: ' + str(e))

    #********** Functions below ******************

    ''' Returns an array of valid country codes '''
    @classmethod
    def GETCOUNTRYCODES(self, req, *args):
        req.clear()
        req.set_status(200)
        req.finish(json.dumps(Locale.Language.All()))

    ''' Here we return a valid country code, based on the language param '''
    @classmethod
    def GETMATCH(self, req, *args):
        try:
            # Get the Payload
            data = json.loads(req.request.body.decode('utf-8'))
            if 'Language' in data:
                # Match the code
                req.clear()
                req.set_status(200)
                req.finish(json.dumps(Locale.Language.Match(data['Language'])))
            else:
                req.set_status(412)
                req.finish('Missing Language in payload?')
        except Exception, e:
            req.set_status(412)
            req.finish('Not a valid payload?')

    ''' Here we return an ordered jason of language:countrycode for all the valid ones '''
    @classmethod
    def GETLANGCODELIST(self, req, *args):
        # Walk the darn module
        all_languages = {}
        cls = dir(Locale.Language)
        for name in cls:
            if name[0] != '_':
                if name not in ['All', 'Match', 'lock']:
                    code = Locale.Language.Match(name)
                    if code != 'xx':
                        all_languages[name] = code
        req.clear()
        req.set_status(200)
        req.finish(json.dumps(all_languages, sort_keys=True))

    ''' Here we return an ordered jason of countrycode:language for all the valid ones '''
    @classmethod
    def GETCODELANGLIST(self, req, *args):
        # Walk the darn module
        all_languages = {}
        cls = dir(Locale.Language)
        for name in cls:
            if name[0] != '_':
                if name not in ['All', 'Match', 'lock']:
                    code = Locale.Language.Match(name)
                    if code != 'xx':
                        all_languages[code] = name
        req.clear()
        req.set_status(200)
        req.finish(json.dumps(all_languages, sort_keys=True))

    ''' Here we return an ordered jason of countrycode:language for all the valid ones in ISO639-3'''
    @classmethod
    def GET3CODELANGLIST(self, req, *args):
        all_languages = {}
        for key, value in ISO639_3.iteritems():
            all_languages[value] = key
        req.clear()
        req.set_status(200)
        req.finish(json.dumps(all_languages, sort_keys=True))

    ''' Here we return an ordered jason of language:countrycode for all the valid ones in ISO639-3'''
    @classmethod
    def GETLANGCODE3LIST(self, req, *args):
        req.clear()
        req.set_status(200)
        req.finish(json.dumps(ISO639_3, sort_keys=True))
