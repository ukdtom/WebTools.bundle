#!/usr/bin/env python
# -*- coding: utf-8 -*-
######################################################################################################################
#					WebTools bundle module for Plex
#
#					HAndles ViewState info about your users on your Plex Media Server
#
#					Author:			dane22, a Plex Community member
#
#					Support thread:	http://forums.plex.tv/discussion/288191
#
######################################################################################################################

import json
from misc import misc
from consts import EXCLUDEELEMENTS, EXCLUDEFIELDS

GET = ['GETVIEWSTATE']
PUT = []
POST = []
DELETE = []

STEPS = 2


class viewstate(object):
    @classmethod
    def init(self):
        return

    '''
    Return viewstate info for a the user
    * Param: section/x (Mandentory)
    * Param: user/userID (optional, if missing, user is the owner)
    '''
    @classmethod
    def GETVIEWSTATE(self, req, *args):
        Log.Debug('Starting getViewState')
        Log.Debug('Arguments are: ' + str(args))
        result = {}
        unwatched = {}
        try:
            # Let's start by checking, if we got the relevant parameters
            user = None
            if args != None:
                # We got additional arguments
                if len(args) > 0:
                    # Get them in lower case
                    arguments = [item.lower() for item in list(args)[0]]
                    # Look for user
                    if 'user' in arguments:
                        try:
                            # Get key of the user
                            user = arguments[arguments.index('user') + 1]
                        except Exception, e:
                            Log.Exception(
                                'Exception in getViewState to digest the user was: %s' % str(e))
                            req.set_status(500)
                            req.finish(
                                'Unknown error digesting the specified user was: %s' % str(e))
                            return
                    # Look for section
                    if 'section' in arguments:
                        try:
                            # Get key of the section
                            section = int(
                                arguments[arguments.index('section') + 1])
                        except Exception, e:
                            Log.Exception(
                                'Exception in getViewState to digest the section was: %s' % str(e))
                            req.set_status(500)
                            req.finish(
                                'Unknown error digesting the specified section was: %s' % str(e))
                            return
                    else:
                        Log.Critical('Missing Section key in parameters')
                        req.set_status(412)
                        req.finish('Missing section parameter')
                        return
                else:
                    Log.Critical('Missing parameters')
                    req.set_status(412)
                    req.finish('Missing parameter')
                    return
            else:
                Log.Critical('Missing parameters')
                req.set_status(412)
                req.finish('Missing parameter')
                return

            # So now user is either none or a keyId
            if user == None:
                print 'Ged 2 User is the owner'
                result['user'] = None
            else:
                # Darn....Hard work ahead..We have to logon as another user here :-(
                print 'Ged3 user is specific'
                result['user'] = user
            # Add some export core info here
            result['section'] = section
            sectionTypeUrl = misc.GetLoopBack() + '/library/sections/' + str(section) + \
                '/all?X-Plex-Container-Start=0&X-Plex-Container-Size=0'
            result['sectionType'] = XML.ElementFromURL(
                sectionTypeUrl).get('viewGroup')
            result['sectionTitle'] = XML.ElementFromURL(
                sectionTypeUrl).get('librarySectionTitle')
            result['serverId'] = XML.ElementFromURL(
                misc.GetLoopBack() + '/identity').get('machineIdentifier')
            # Now let's walk the actual section, in small steps, and add to the result
            url = misc.GetLoopBack() + '/library/sections/' + str(section) + \
                '/all?unwatched!=1&' + EXCLUDEELEMENTS + '&' + \
                EXCLUDEFIELDS + '&X-Plex-Container-Start='
            start = 0
            medias = {}
            while True:
                fetchUrl = url + str(start) + \
                    '&X-Plex-Container-Size=' + str(STEPS)

                unwatchedXML = XML.ElementFromURL(fetchUrl)
                for media in unwatchedXML.xpath('Video'):

                    print 'Ged madia', media.get('title')
                    title = media.get('title')
                    ratingKey = media.get('ratingKey')
                    medias[media.get('title')] = int(media.get('ratingKey'))

                start += STEPS
                if int(unwatchedXML.get('size')) == 0:
                    break

            print 'Ged search url', url
            result['unwatched'] = medias

            req.set_status(200)
            req.set_header('Content-Type', 'application/json; charset=utf-8')
            req.finish(json.dumps(result))
        except Exception, e:
            Log.Exception('Exception in getViewState was %s' % str(e))
            req.set_status(500)
            req.finish('Unknown error was %s' % str(e))

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
