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
import re
from misc import misc
from wtV3 import wtV3
from consts import EXCLUDEELEMENTS, EXCLUDEFIELDS, DEBUGMODE, MEDIATYPE

GET = ['GETSECTIONSLIST', 'GETSTATUS', 'GETRESULT']
PUT = ['ABORT', 'UPDATEAGENT']
POST = []
DELETE = []

# Consts used here
# Supported sections
SUPPORTEDSECTIONS = ['movie', 'show']
# Internal tracker of where we are
runningState = 0
# Flag to set if user wants to cancel
bAbort = False
# Amount of chuncks to grab
MediaChuncks = 40
# Response to getStatus
statusMsg = wtV3().GETTRANSLATE(None, None, Internal=True, String='idle')
# Minimum score
MinScore = 95
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
            bForce = ('force' in arguments)
        else:
            Log.Critical('Missing Arguments')
            req.clear()
            req.set_status(412)
            req.finish('Missing Arguments')
        # So far so good, we got a section key
        Agent = self.getPrimaryAgent(key)
        ChangedOK = []
        ChangedErr = []
        self.scanItems(req, key, Agent, Force=bForce)

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
    def scanItems(self, req, sectionNumber, Agent, Force=False):
        print 'Ged Force', Force
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
                    Force=Force,
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
        print 'Ged51 episodes', str(totalSize)
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


def scanMedias(sectionNumber, sectionType, req, agent=None, Force=False):
    """Scan db and files. Must run as a thread"""
    global runningState
    global statusMsg
    try:
        if sectionType == 'movie':
            scanMovieDb(sectionNumber=sectionNumber, agent=agent, Force=Force)
        elif sectionType == 'show':
            print 'Ged show'
            scanShowDB(sectionNumber=sectionNumber, agent=agent, Force=Force)
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
    try:
        result = False
        print 'ged 101', url
        SearchResults = XML.ElementFromURL(url).xpath('//SearchResult')
        print 'ged 102'
        Log.Info(
            'Found %s possibillities for %s' % (len(SearchResults), title))
        # for SearchResult in SearchResults:
        SearchResult = SearchResults[0]
        print 'ged 103'
        # Check if there's an year in the title, and if so, remove it
        match = re.match(r'.*([1-2][0-9]{3})', title)
        if match is not None:
            # Then it found a match!
            title = title.replace(match.group(1), '')
            title = re.sub("\(|\)|\[|\]", "", title).strip()
        print 'Ged 104'
        if year == SearchResult.get('year'):
            if title == SearchResult.get('name'):
                if int(SearchResult.get('score')) >= MinScore:
                    print 'ged 55', String.Quote(SearchResult.get('guid'))
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
                        print 'Ged 105'
                        break
                    except Exception, e:
                        Log.Exception(
                            'Exception happened in \
                            updateMediaAgent was %s' % str(e))
                        ChangedErr.append(unicode(title, "utf-8"))
                        result = False
                else:
                    Log.Info(
                        'Updating failed, since a score of %s %' % SearchResult.get('score'))
                    Log.Info('is below the minimum of %s %' % MinScore)
        if not result:
            Log.Info('Could not find any match for: %s', title)
            ChangedErr.append(title)
    except Exception, e:
        Log.Exception('Exception in updateMediaAgent was %s' % str(e))


def scanShowDB(sectionNumber=0, agent=None, Force=False):
    """Scan Episodes from the database"""
    global statusMsg
    global runningState
    try:
        Log.Debug(
            'Starting scanShowDB for section %s' % (
                sectionNumber))
        runningState = -1
        statusMsg = wtV3().GETTRANSLATE(
            None, Internal=True,
            String='Starting to scan database for section %s')\
            % (sectionNumber)
        # Start by getting the totals of episodes for this section
        urlSize = ''.join((
            misc.GetLoopBack(),
            '/library/sections/',
            sectionNumber,
            '/all?X-Plex-Container-Start=1',
            '&X-Plex-Container-Size=0',
            '&type=',
            str(MEDIATYPE['Episode'])
        ))
        totalSize = XML.ElementFromURL(urlSize).get('totalSize')
        AmountOfMediasInDatabase = totalSize
        Log.Debug('Total size of medias are %s' % (totalSize))
        iEpisode = 0
        iCEpisode = 0
        statusEpisodes = wtV3().GETTRANSLATE(
            None, Internal=True,
            String='Scanning database episodes %s of %s :')\
            % (iEpisode, totalSize)
        statusMsg = statusEpisodes
        # So let's walk the library
        while True:
            # Grap Episodes
            urlEpisodes = ''.join((
                misc.GetLoopBack(),
                '/library/sections/',
                sectionNumber,
                '/all?excludeElements=',
                EXCLUDEELEMENTS,
                '&excludeFields=',
                EXCLUDEFIELDS,
                '&X-Plex-Container-Start=',
                str(iCEpisode),
                '&X-Plex-Container-Size=',
                str(MediaChuncks),
                '&type=',
                str(MEDIATYPE['Episode'])
            ))
            print 'Ged 61 urlEpisodes', urlEpisodes

            episodes = XML.ElementFromURL(urlEpisodes).xpath('//Video')
            # Grap individual shows
            for episode in episodes:
                urlEpisode = ''.join((
                    misc.GetLoopBack(),
                    '/library/metadata/',
                    episode.get('ratingKey'),
                    '?excludeElements=',
                    EXCLUDEELEMENTS,
                    '&excludeFields=',
                    EXCLUDEFIELDS
                ))
                print 'Ged 81', urlEpisode
                currentEpisode = XML.ElementFromURL(
                    urlEpisode).xpath('//Video')[0]
                title = currentEpisode.get('title')
                guid = currentEpisode.get('guid')
                # year = currentShow.get('year')
                # key = currentShow.get('ratingKey')
                statusMsg = 'investigating episode: %s' % (
                    title)
                Log.Info(statusMsg)
                key = episode.get('ratingKey')
                year = episode.get('year')

                print 'GED KIG HER'
                # Store show id in a list. and afterwards, fix each show one by one
                statusMsg = 'Updating show: %s' % (
                    title)
                if agent not in guid:
                    Log.Info(statusMsg)
                    print 'Ged updating', title
                    # key = show.get('ratingKey')
                    # year = show.get('year')
                    updateMediaAgent(key, agent, year, title)
                elif Force:
                    Log.Info(statusMsg)
                    print 'Ged Key', key
                    print 'Ged Agent', agent
                    print 'Ged Year', year
                    print 'Ged Title', title
                    updateMediaAgent(key, agent, year, title)
                else:
                    Log.Info('Episode: %s is okay' % title)
            iCEpisode += MediaChuncks
            if len(episodes) == 0:
                strMsg = (
                    'Scanning database: %s : Done'
                    % (str(totalSize)))
                statusMsg = wtV3().GETTRANSLATE(
                    None, Internal=True,
                    String=strMsg)
                Log.Debug('***** Done scanning the database *****')
                runningState = 1
                break
        return
    except ValueError:
        statusMsg = wtV3().GETTRANSLATE(
            None, Internal=True,
            String='Idle')
        runningState = 99
        Log.Info('Aborted in ScanShowDB')
    except Exception, e:
        Log.Exception('Fatal error in scanShowDB: ' + str(e))
        runningState = 99
