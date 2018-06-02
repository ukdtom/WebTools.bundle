###############################################################################
# Change Item Agent unit
# A WebTools bundle plugin
#
# Used to update agent on items in a library
#
# Author: dane22, a Plex Community member
#
# Credits: Full credits goes to Chris Allen for getting the idea, and
# providing the initial code
#
###############################################################################

import json
from misc import misc
from wtV3 import wtV3
from consts import EXCLUDEELEMENTS, EXCLUDEFIELDS, DEBUGMODE

GET = ['GETSECTIONSLIST', 'GETSTATUS', 'GETRESULT']
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
# Amount of chuncks to grab
MediaChuncks = 40
# Medias updated
MediasUpdated = []
# Response to getStatus
statusMsg = wtV3().GETTRANSLATE(None, None, Internal=True, String='idle')
# Minimum score
MinScore = 97
# Results
ChangedOK = []
ChangedErr = []


class changeagent(object):
    # Make sure init only run once
    init_already = False

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
        global ChangedErr
        global ChangedOK
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
            # Get section Key
            if 'key' in arguments:
                # Get key of the user
                key = arguments[arguments.index('key') + 1]
            else:
                Log.Error('Missing key of section')
                req.clear()
                req.set_status(412)
                req.finish('Missing key of section')
        else:
            Log.Critical('Missing Arguments')
            req.clear()
            req.set_status(412)
            req.finish('Missing Arguments')
        # So far so good, we got a section key
        Agent = self.getPrimaryAgent(key)
        ChangedOK = []
        ChangedErr = []
        self.scanItems(req, key, Agent)

    @classmethod
    def GETSECTIONSLIST(self, req, *args):
        """Get supported Section list"""
        Log.Debug('getSectionsList requested')
        try:
            Sections = misc.getSectionList(SUPPORTEDSECTIONS)
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

    @classmethod
    def GETRESULT(self, req, *args):
        """Return the result"""
        # Are we in idle mode?
        if runningState == 0:
            req.clear()
            Log.Info('Changed OK are: ' + str(ChangedOK))
            Log.Info('Changed Error are: ' + str(ChangedErr))
            retMsg = {}
            retMsg['OK'] = ChangedOK
            retMsg['Error'] = ChangedErr
            req.set_status(200)
            req.set_header(
                'Content-Type', 'application/json; charset=utf-8')
            req.finish(json.dumps(retMsg))
        elif runningState == 99:
            if bAbort:
                req.set_status(204)
            else:
                req.set_status(204)
        else:
            req.clear()
            req.set_status(204)
        return

# ################## Internal functions #############################

    @classmethod
    def scanItems(self, req, sectionNumber, Agent):
        """Scan db. Must run as a thread"""
        try:
            # Let's find out the info of section here
            url = misc.GetLoopBack() + '/library/sections/'
            response = XML.ElementFromURL(url).xpath(
                '//Directory[@key=' + sectionNumber + ']')
            sectionTitle = response[0].get('title')
            sectionType = response[0].get('type')
            strMsg = ''.join((
                'Going to scan section',
                sectionNumber,
                ' with a title of ',
                sectionTitle,
                ' and a type of ',
                sectionType))
            Log.Debug(strMsg)
            if runningState in [0, 99]:
                Thread.Create(
                    scanMedias, globalize=True,
                    sectionNumber=sectionNumber,
                    sectionType=sectionType,
                    agent=Agent,
                    req=req)
            else:
                req.clear()
                req.set_status(409)
                req.finish('Scanning already in progress')
        except Exception, ex:
            Log.Exception('Fatal error happened in scanItems: ' + str(ex))
            req.clear()
            req.set_status(500)
            req.finish('Fatal error happened in scanItems: ' + str(ex))
            return req

    @classmethod
    def getPrimaryAgent(self, section):
        # Get the primary agent for the library
        url = ''.join((
            misc.GetLoopBack(),
            '/library/sections'))
        try:
            Scanner = XML.ElementFromURL(url).xpath(
                '//Directory[@key="' + section + '"]/@agent')[0]
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


def scanMovieDb(sectionNumber=0, agent=None):
    """Get a list of all files in a Movie Library from the database"""
    global AmountOfMediasInDatabase
    global statusMsg
    global runningState
    global MediasUpdated
    try:
        Log.Debug(
            'Starting scanMovieDb for section %s' % (sectionNumber))
        runningState = -1
        strStatus = (
            'Starting to scan database for section %s'
            % sectionNumber)
        statusMsg = (
            wtV3().GETTRANSLATE(
                None, Internal=True,
                String=strStatus))
        # Start by getting the totals of this section
        totalSize = XML.ElementFromURL(
            misc.GetLoopBack() + '/library/sections/' + sectionNumber +
            '/all?X-Plex-Container-Start=1&X-Plex-Container-Size=0')\
            .get('totalSize')
        AmountOfMediasInDatabase = totalSize
        Log.Debug('Total size of medias are %s' % (totalSize))
        iStart = 0
        iCount = 0
        strMsg = 'Scanning database: item %s of %s : \
        Working' % (iCount, totalSize)
        statusMsg = wtV3().GETTRANSLATE(
            None, Internal=True, String=strMsg)
        # So let's walk the library
        while True:
            # Grap a chunk of videos from the server
            medias = XML.ElementFromURL(
                misc.GetLoopBack() + '/library/sections/' + sectionNumber +
                '/all?X-Plex-Container-Start=' + str(iStart) +
                '&X-Plex-Container-Size=' + str(MediaChuncks) +
                '&excludeElements=' + EXCLUDEELEMENTS +
                '&excludeFields=' + EXCLUDEFIELDS).xpath('//Video')
            for video in medias:
                iCount += 1
                videoUrl = ''.join((
                    misc.GetLoopBack(),
                    video.get('key'),
                    '?excludeElements=' + EXCLUDEELEMENTS,
                    '&excludeFields=' + EXCLUDEFIELDS
                ))
                guid = XML.ElementFromURL(
                    videoUrl).xpath('//Video')[0].get('guid')
                if agent not in guid:
                    MediasUpdated.append(video.get('title'))
                    Log.Info('Need to update media: %s' % video.get('title'))
                    updateMediaAgent(
                        video.get('ratingKey'),
                        agent,
                        video.get('year'),
                        video.get('title'))
                # Did user abort?
                if bAbort:
                    runningState = 0
                    raise ValueError('Aborted')
                    break
                strMsg = 'Scanning database: item %s of %s : \
                Working' % (iCount, totalSize)
                statusMsg = wtV3().GETTRANSLATE(
                    None, Internal=True,
                    String=strMsg)
            iStart += MediaChuncks
            if len(medias) == 0:
                statusMsg = 'Scanning database: %s : Done' % (
                    totalSize)
                Log.Info('***** Done scanning the database *****')
                runningState = 1
                break
        return
    except Exception, e:
        Log.Exception(
                'Exception Fatal error in scanMovieDb: ' + str(e))
        runningState = 99


def scanMedias(sectionNumber, sectionType, req, agent=None):
    """Scan db and files. Must run as a thread"""
    global runningState
    global statusMsg
    try:
        if sectionType == 'movie':
            scanMovieDb(sectionNumber=sectionNumber, agent=agent)
        elif sectionType == 'show':
            print 'Ged show'
            # self.scanShowDB(sectionNumber=sectionNumber, agent=agent)
        else:
            req.clear()
            req.set_status(400)
            req.finish('Unknown Section Type')
        if bAbort:
            raise ValueError('Aborted')
        statusMsg = wtV3().GETTRANSLATE(
            None, Internal=True,
            String='Scanning Library')
        runningState = 0
        statusMsg = 'done'
    except ValueError:
        Log.Info('Aborted in ScanMedias')
    except Exception, e:
        Log.Exception('Exception happend in scanMedias: ' + str(e))
        statusMsg = wtV3().GETTRANSLATE(
            self, None, Internal=True, String='Idle')


def updateMediaAgent(key, agent, year, title):
    global ChangedErr
    global ChangedOK
    url = ''.join((
        misc.GetLoopBack(),
        '/library/metadata/',
        key,
        '/matches?agent=',
        agent,
        '&manual=0'
    ))
    result = False
    SearchResults = XML.ElementFromURL(url).xpath('//SearchResult')
    for SearchResult in SearchResults:
        if year == SearchResult.get('year'):
            if title == SearchResult.get('name'):
                if int(SearchResult.get('score')) >= MinScore:
                    updateurl = ''.join((
                        misc.GetLoopBack(),
                        '/library/metadata/',
                        key,
                        '/match?guid=',
                        String.Quote(SearchResult.get('guid')),
                        '&name=',
                        String.Quote(SearchResult.get('name'))
                    ))
                    try:
                        result = HTTP.Request(
                            url=updateurl,
                            method='PUT',
                            immediate=True,
                            timeout=5)
                        ChangedOK.append(unicode(title, "utf-8"))
                        result = True
                        break
                    except Exception, e:
                        ChangedErr.append(unicode(title, "utf-8"))
                        result = False
                        break
    if not result:
        ChangedErr.append(title)
