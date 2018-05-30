###############################################################################
# Change Item Agent unit
# A WebTools bundle plugin
#
# Used to update agent on items in a library
#
# Author: dane22, a Plex Community member
#
###############################################################################

import json
from misc import misc

GET = ['GETSECTIONSLIST', 'GETSTATUS']
PUT = ['ABORT', 'UPDATEAGENT']
POST = []
DELETE = []

# Consts used here
# Supported sections
SUPPORTEDSECTIONS = ['movie']
# Internal tracker of where we are
runningState = 0
# Flag to set if user wants to cancel
bAbort = False


class changeagent(object):
    init_already = False							# Make sure init only run once

    @classmethod
    def init(self):
        """Init of the class"""
        return

    @classmethod
    def GETSTATUS(self, req, *args):
        """Return current status"""
        req.clear()
        req.set_status(200)
        if runningState == 0:
            req.finish('Idle')
        else:
            req.finish(statusMsg)

    @classmethod
    def ABORT(self, req, *args):
        """Abort"""
        global runningState
        runningState = 0
        global bAbort
        bAbort = True
        req.clear()
        req.set_status(200)

    @classmethod
    def UPDATEAGENT(self, req, *args):
        print 'Ged Update Agent called'
        # Start by getting the key of the Section
        if args is not None:
            # We got additional arguments
            if len(args) > 0:
                # Get them in lower case
                arguments = [item.lower() for item in list(args)[0]]
            else:
                Log.Critical('Missing Arguments')
                req.clear()
                req.set_status(412)
                req.finish('Missing Arguments')
            # Get playlist Key
            if 'key' in arguments:
                # Get key of the user
                key = arguments[arguments.index('key') + 1]
            else:
                Log.Error('Missing key of playlist')
                req.clear()
                req.set_status(412)
                req.finish('Missing key of playlist')
        else:
            Log.Critical('Missing Arguments')
            req.clear()
            req.set_status(412)
            req.finish('Missing Arguments')
        # So far so good, we got a section key
        Agent = self.getPrimaryAgent(key)
        print 'Ged33', Agent

    @classmethod
    def GETSECTIONSLIST(self, req, *args):
        """Get supported Section list"""
        Log.Debug('getSectionsList requested')
        try:
            rawSections = XML.ElementFromURL(
                misc.GetLoopBack() + '/library/sections')
            Sections = []
            for directory in rawSections:
                if directory.get('type') in SUPPORTEDSECTIONS:
                    Section = {
                        'key': directory.get('key'),
                        'title': directory.get('title'),
                        'type': directory.get('type')}
                    Sections.append(Section)
            req.clear()
            req.set_status(200)
            req.set_header('Content-Type', 'application/json; charset=utf-8')
            req.finish(json.dumps(Sections))
        except Exception, e:
            Log.Exception(
                'Fatal error happened in getSectionsList: %s' % (str(e)))
            req.clear()
            req.set_status(500)
            req.finish('Fatal error happened in getSectionsList')

# ################## Internal functions #############################

    @classmethod
    def getPrimaryAgent(self, section):
        # Get the primary agent for the library
        url = ''.join((
            misc.GetLoopBack(),
            '/library/sections'))
        try:
            Scanner = XML.ElementFromURL(url).xpath(
                '//Directory[@key="' + section + '"]/@scanner')[0]
            return Scanner
        except Exception, e:
            Log.Exception('Exception in PlayList orderList was %s' % (str(e)))

    @classmethod
    def getFunction(self, metode, req, *args):
        """Get the relevant function and call it with optinal params"""
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
        if self.function is None:
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
                if params is None:
                    getattr(self, self.function)(req)
                else:
                    getattr(self, self.function)(req, params)
            except Exception, e:
                Log.Exception('Exception in process of: ' + str(e))
