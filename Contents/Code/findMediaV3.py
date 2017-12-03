######################################################################################################################
#	findMedia unit
# A WebTools bundle plugin
#
# Used to locate both items missing from the database, as well as from the filesystem
#
#	Author: dane22, a Plex Community member
#
######################################################################################################################

import urllib
import unicodedata
import json
import time
import sys
import os
from consts import DEBUGMODE, VALIDEXT
from misc import misc
from wtV3 import wtV3

# Consts used here
# Int of amount of medias in a database section
AmountOfMediasInDatabase = 0
# Files from the database
mediasFromDB = []
# Files from the file system
mediasFromFileSystem = []
# Unmatched items
unmatchedByPlex = []
# Response to getStatus
statusMsg = wtV3().GETTRANSLATE(None, None, Internal=True, String='idle')
# Internal tracker of where we are
runningState = 0
# Flag to set if user wants to cancel
bAbort = False
Extras = ['behindthescenes', 'deleted', 'featurette', 'interview',
          'scene', 'short', 'trailer']														# Local extras
ExtrasDirs = ['behind the scenes', 'deleted scenes', 'featurettes',
              'interviews', 'scenes', 'shorts', 'trailers']		# Directories to be ignored
Specials = ['season 00', 'season 0', 'specials']                # Specials dirs
# Valid keys for prefs
KEYS = ['IGNORE_HIDDEN', 'IGNORED_DIRS', 'VALID_EXTENSIONS', 'IGNORE_SPECIALS']
excludeElements = 'Actor,Collection,Country,Director,Genre,Label,Mood,Producer,Role,Similar,Writer'
excludeFields = 'summary,tagline'
SUPPORTEDSECTIONS = ['movie', 'show']

GET = ['SCANSECTION', 'GETSECTIONSLIST',
       'GETRESULT', 'GETSTATUS', 'GETSETTINGS']
PUT = ['ABORT', 'RESETSETTINGS']
POST = ['SETSETTINGS']
DELETE = []


class findMediaV3(object):
    init_already = False							# Make sure init only run once
    bResultPresent = False						# Do we have a result to present

    # Init of the class
    @classmethod
    def init(self):
        global retMsg
        global MediaChuncks
        global CoreUrl
        global init_already
        try:
            # Only init once during the lifetime of this
            if not self.init_already:
                self.init_already = True
                retMsg = ['WebTools']
                self.populatePrefs()
                Log.Debug('******* Starting findMedia *******')
                Log.Debug('********* Prefs are ***********')
                Log.Debug(Dict['findMedia'])
            self.MediaChuncks = 40
            self.CoreUrl = misc.GetLoopBack() + '/library/sections/'
        except Exception, e:
            Log.Exception('Exception in FM Init was %s' % (str(e)))

    #********** Functions below ******************

    # Set settings
    @classmethod
    def SETSETTINGS(self, req, *args):
        try:
            # Get the Payload
            data = json.loads(req.request.body.decode('utf-8'))
        except Exception, e:
            Log.Exception('Not a valid payload: ' + str(e))
            req.set_status(412)
            req.finish('Not a valid payload?')
        try:
            Log.Debug('setSettings called with a body of: ' + str(data))
            # Walk the settings body, and only accept valid settings
            if 'IGNORE_HIDDEN' in data:
                Dict['findMedia']['IGNORE_HIDDEN'] = data['IGNORE_HIDDEN']
            if 'IGNORE_SPECIALS' in data:
                Dict['findMedia']['IGNORE_SPECIALS'] = data['IGNORE_SPECIALS']
            if 'IGNORED_DIRS' in data:
                Dict['findMedia']['IGNORED_DIRS'] = data['IGNORED_DIRS']
            if 'VALID_EXTENSIONS' in data:
                Dict['findMedia']['VALID_EXTENSIONS'] = data['VALID_EXTENSIONS']
            if 'IGNORE_EXTRAS' in data:
                Dict['findMedia']['IGNORE_EXTRAS'] = data['IGNORE_EXTRAS']
            Dict.Save()
        except Exception, e:
            Log.Exception('Exception in setSettings: ' + str(e))
            req.clear()
            req.set_status(500)
            req.finish('Fatal error in setSettings was: ' + str(e))

    # Main call for class.....
    @classmethod
    def SCANSECTION(self, req, *args):
        global AmountOfMediasInDatabase
        global retMsg
        global bAbort
        retMsg = ['WebTools']
        bAbort = False

        # Scan shows from the database
        def scanShowDB(sectionNumber=0):
            global AmountOfMediasInDatabase
            global mediasFromDB
            global statusMsg
            global runningState
            global unmatchedByPlex
            try:
                Log.Debug('Starting scanShowDB for section %s' %
                          (sectionNumber))
                unmatchedByPlex = []
                runningState = -1
                statusMsg = wtV3().GETTRANSLATE(self, None, Internal=True,
                                                String='Starting to scan database for section %s') % (sectionNumber)
                # Start by getting the totals of this section
                totalSize = XML.ElementFromURL(
                    self.CoreUrl + sectionNumber + '/all?X-Plex-Container-Start=1&X-Plex-Container-Size=0').get('totalSize')
                AmountOfMediasInDatabase = totalSize
                Log.Debug('Total size of medias are %s' % (totalSize))
                iShow = 0
                iCShow = 0
                statusShows = wtV3().GETTRANSLATE(self, None, Internal=True,
                                                  String='Scanning database show %s of %s :') % (iShow, totalSize)
                statusMsg = statusShows
                # So let's walk the library
                while True:
                    # Grap shows
                    urlShows = self.CoreUrl + sectionNumber + '/all?X-Plex-Container-Start=' + str(iCShow) + '&X-Plex-Container-Size=' + str(
                        self.MediaChuncks) + '&excludeElements=' + excludeElements + '&excludeFields=' + excludeFields
                    shows = XML.ElementFromURL(urlShows).xpath('//Directory')
                    # Grap individual show
                    for show in shows:
                        statusShow = show.get('title')
                        statusMsg = statusShows + statusShow
                        iSeason = 0
                        iCSeason = 0
                        # Grap seasons
                        while True:
                            seasons = XML.ElementFromURL(misc.GetLoopBack() + show.get('key') + '?X-Plex-Container-Start=' + str(iCSeason) + '&X-Plex-Container-Size=' + str(
                                self.MediaChuncks) + '&excludeElements=' + excludeElements + '&excludeFields=' + excludeFields).xpath('//Directory')
                            # Grap individual season
                            for season in seasons:
                                if season.get('title') == 'All episodes':
                                    iSeason += 1
                                    continue
                                statusSeason = ' ' + season.get('title')
                                statusMsg = statusShows + statusShow + statusSeason
                                iSeason += 1
                                # Grap Episodes
                                iEpisode = 0
                                iCEpisode = 0
                                while True:
                                    url = misc.GetLoopBack() + season.get('key') + '?X-Plex-Container-Start=' + str(iCEpisode) + '&X-Plex-Container-Size=' + \
                                        str(self.MediaChuncks) + '&excludeElements=' + \
                                        excludeElements + '&excludeFields=' + excludeFields
                                    videos = XML.ElementFromURL(
                                        url).xpath('//Video')
                                    for video in videos:
                                        if bAbort:
                                            raise ValueError('Aborted')
                                        bUnmatched = False
                                        if video.get('year') == None:
                                            # Also check if summary is missing, since else, it might be a false alert
                                            if (video.get('summary') == None) or (video.get('summary') == ""):
                                                bUnmatched = True
                                                # No year nor summary, so most likely a mismatch
                                                key = video.get('ratingKey')
                                                unmatchedURL = misc.GetLoopBack() + '/library/metadata/' + key + '?excludeElements=' + \
                                                    excludeElements + '&excludeFields=' + excludeFields
                                                unmatched = XML.ElementFromURL(
                                                    unmatchedURL).xpath('//Video')
                                                filename = unmatched[0].xpath(
                                                    '//Part/@file')[0]
                                                if self.addThisItem(filename, 'video'):
                                                    Log.Info(
                                                        'Unmatched file confirmed as %s' % filename)
                                                    unmatchedByPlex.append(
                                                        filename.encode("utf-8"))
                                        episodes = XML.ElementFromString(
                                            XML.StringFromElement(video)).xpath('//Part')
                                        for episode in episodes:
                                            if bAbort:
                                                raise ValueError('Aborted')
                                            filename = episode.get('file')
                                            filename = String.Unquote(
                                                filename).encode('utf8', 'ignore')
                                            if self.addThisItem(filename, 'video'):
                                                mediasFromDB.append(
                                                    filename.encode("utf-8"))
                                            iEpisode += 1
                                        # Inc Episodes counter
                                    iCEpisode += self.MediaChuncks
                                    if len(videos) == 0:
                                        break
                            # Inc Season counter
                            iCSeason += self.MediaChuncks
                            if len(seasons) == 0:
                                break
                        iShow += 1
                        statusShows = wtV3().GETTRANSLATE(self, None, Internal=True,
                                                          String='Scanning database show %s of %s :') % (str(iShow), str(totalSize))
                    # Inc. Shows counter
                    iCShow += self.MediaChuncks
                    if len(shows) == 0:
                        statusMsg = wtV3().GETTRANSLATE(self, None, Internal=True,
                                                        String='Scanning database: %s : Done') % (str(totalSize))
                        Log.Debug('***** Done scanning the database *****')
                        if DEBUGMODE:
                            Log.Debug(mediasFromDB)
                        runningState = 1
                        break
                return
            except ValueError:
                statusMsg = wtV3().GETTRANSLATE(self, None, Internal=True, String='Idle')
                runningState = 99
                Log.Info('Aborted in ScanShowDB')
            except Exception, e:
                Log.Exception('Fatal error in scanShowDB: ' + str(e))
                runningState = 99
        # End scanShowDB

        # Find missing files from the database
        def findMissingFromDB():
            global MissingFromDB
            Log.Debug('Finding items missing from Database')
            MissingFromDB = []
            try:
                for item in mediasFromFileSystem:
                    if bAbort:
                        raise ValueError('Aborted')
                    if item not in mediasFromDB:
                        MissingFromDB.append(item)
                return MissingFromDB
            except ValueError:
                Log.Info('Aborted in findMissingFromDB')

        # Find missing files from the filesystem
        def findMissingFromFS():
            global MissingFromFS
            Log.Debug('Finding items missing from FileSystem')
            MissingFromFS = []
            try:
                for item in mediasFromDB:
                    if bAbort:
                        raise ValueError('Aborted')
                    if item not in mediasFromFileSystem:
                        MissingFromFS.append(item)
                return MissingFromFS
            except ValueError:
                Log.Info('Aborted in findMissingFromFS')

        # Scan the file system
        def getFiles(filePath, mediaType):
            global mediasFromFileSystem
            global runningState
            global statusMsg
            try:
                runningState = -1
                Log.Debug(
                    "*********************** FileSystem scan Paths: *****************************************")
                bScanStatusCount = 0
                # for filePath in files:
                for Path in filePath:
                    # Decode filePath
                    bScanStatusCount += 1
                    filePath2 = urllib.unquote(Path).decode('utf8')
                    filePath2 = misc.Unicodize(filePath2)
                    Log.Debug("Handling filepath #%s: %s" % (
                        bScanStatusCount, filePath2.encode('utf8', 'ignore')))
                    try:
                        for root, subdirs, files in os.walk(filePath2):
                            for file in files:
                                filename = Core.storage.join_path(root, file)
                                file = misc.Unicodize(filename).encode('utf8')
                                if self.addThisItem(filename, mediaType):
                                    if Platform.OS == 'Windows':
                                        # I hate windows
                                        pos = filename.find(':') - 1
                                        if pos != -2:
                                            # We dont got an UNC path here
                                            filename = filename[pos:]
                                    Log.Debug('appending file: ' + filename)
                                    mediasFromFileSystem.append(
                                        filename.encode("utf-8"))
                                if DEBUGMODE:
                                    Log.Debug('Scanning file: ' + file)
                                statusMsg = wtV3().GETTRANSLATE(self, None, Internal=True,
                                                                String='Scanning file: %s') % file
                    except Exception, e:
                        Log.Exception(
                            'Exception happened in FM scanning filesystem: ' + str(e))
                        return
                    Log.Debug('***** Finished scanning filesystem *****')
                    if DEBUGMODE:
                        Log.Debug(mediasFromFileSystem)
                    runningState = 2
            except ValueError:
                statusMsg = wtV3().GETTRANSLATE(self, None, Internal=True, String='Idle')
                runningState = 0
                Log.Info('Aborted in getFiles')
            except Exception, e:
                Log.Exception('Exception happend in getFiles: ' + str(e))
                runningState = 99

        # Get a list of all files in a Movie Library from the database
        def scanMovieDb(sectionNumber=0):
            global AmountOfMediasInDatabase
            global mediasFromDB
            global unmatchedByPlex
            global statusMsg
            global runningState
            try:
                unmatchedByPlex = []
                Log.Debug('Starting scanMovieDb for section %s' %
                          (sectionNumber))
                runningState = -1
                statusMsg = wtV3().GETTRANSLATE(self, None, Internal=True,
                                                String='Starting to scan database for section %s') % sectionNumber
                # Start by getting the totals of this section
                totalSize = XML.ElementFromURL(
                    self.CoreUrl + sectionNumber + '/all?X-Plex-Container-Start=1&X-Plex-Container-Size=0').get('totalSize')
                AmountOfMediasInDatabase = totalSize
                Log.Debug('Total size of medias are %s' % (totalSize))
                iStart = 0
                iCount = 0
                statusMsg = wtV3().GETTRANSLATE(self, None, Internal=True,
                                                String='Scanning database: item %s of %s : Working') % (iCount, totalSize)
                # So let's walk the library
                while True:
                    # Grap a chunk of videos from the server
                    medias = XML.ElementFromURL(self.CoreUrl + sectionNumber + '/all?X-Plex-Container-Start=' + str(iStart) + '&X-Plex-Container-Size=' + str(
                        self.MediaChuncks) + '&excludeElements=' + excludeElements + '&excludeFields=' + excludeFields).xpath('//Video')
                    for video in medias:
                        iCount += 1
                        year = video.get('year')
                        if year == None:
                            # No year, so most likely a mismatch
                            key = video.get('ratingKey')
                            unmatchedURL = misc.GetLoopBack() + '/library/metadata/' + key + '?excludeElements=' + \
                                excludeElements + '&excludeFields=' + excludeFields
                            unmatched = XML.ElementFromURL(
                                unmatchedURL).xpath('//Video')
                            filename = unmatched[0].xpath(
                                '//Part/@file')[0]
                            if self.addThisItem(filename, 'video'):
                                Log.Info(
                                    'Unmatched file confirmed as %s' % filename)
                                unmatchedByPlex.append(
                                    filename.encode("utf-8"))
                        parts = XML.ElementFromString(
                            XML.StringFromElement(video)).xpath('//Part')
                        # Walk the parts of a media
                        for part in parts:
                            if bAbort:
                                runningState = 0
                                raise ValueError('Aborted')
                                break
                            filename = part.get('file')
                            filename = unicode(misc.Unicodize(
                                part.get('file')).encode('utf8', 'ignore'))
                            if self.addThisItem(filename, 'video'):
                                mediasFromDB.append(filename.encode("utf-8"))
                            statusMsg = wtV3().GETTRANSLATE(self, None, Internal=True,
                                                            String='Scanning database: item %s of %s : Working') % (iCount, totalSize)
                    iStart += self.MediaChuncks
                    if len(medias) == 0:
                        statusMsg = 'Scanning database: %s : Done' % (
                            totalSize)
                        Log.Debug('***** Done scanning the database *****')
                        if DEBUGMODE:
                            Log.Debug(mediasFromDB)
                        runningState = 1
                        break

                    '''
                    # Grap a chunk from the server
                    medias = XML.ElementFromURL(self.CoreUrl + sectionNumber + '/all?X-Plex-Container-Start=' + str(iStart) + '&X-Plex-Container-Size=' + str(
                        self.MediaChuncks) + '&excludeElements=' + excludeElements + '&excludeFields=' + excludeFields).xpath('//Part')
                    # Walk the chunk
                    for part in medias:
                        if bAbort:
                            runningState = 0
                            raise ValueError('Aborted')
                            break
                        iCount += 1
                        filename = part.get('file')
                        filename = unicode(misc.Unicodize(
                            part.get('file')).encode('utf8', 'ignore'))
                        mediasFromDB.append(filename)
                        statusMsg = wtV3().GETTRANSLATE(self, None, Internal=True,
                                         String='Scanning database: item %s of %s : Working') % (iCount, totalSize)
                    iStart += self.MediaChuncks
                    if len(medias) == 0:
                        statusMsg = 'Scanning database: %s : Done' % (
                            totalSize)
                        Log.Debug('***** Done scanning the database *****')
                        if DEBUGMODE:
                            Log.Debug(mediasFromDB)
                        runningState = 1
                        break
                    '''
                return
            except Exception, e:
                Log.Exception('Fatal error in scanMovieDb: ' + str(e))
                runningState = 99
        # End scanMovieDb

        # Scan db and files. Must run as a thread
        def scanMedias(sectionNumber, sectionLocations, sectionType, req):
            global runningState
            global statusMsg
            global retMsg
            try:
                if sectionType == 'movie':
                    MediaType = 'video'
                    scanMovieDb(sectionNumber=sectionNumber)
                elif sectionType == 'show':
                    MediaType = 'video'
                    scanShowDB(sectionNumber=sectionNumber)
                else:
                    req.clear()
                    req.set_status(400)
                    req.finish('Unknown Section Type')
                if bAbort:
                    raise ValueError('Aborted')
                getFiles(sectionLocations, MediaType)
                if bAbort:
                    raise ValueError('Aborted')
                retMsg = {}
                statusMsg = wtV3().GETTRANSLATE(self, None, Internal=True,
                                                String='Get missing from File System')
                retMsg["MissingFromFS"] = findMissingFromFS()
                if bAbort:
                    raise ValueError('Aborted')
                statusMsg = wtV3().GETTRANSLATE(self, None, Internal=True,
                                                String='Get missing from database')
                retMsg["MissingFromDB"] = findMissingFromDB()
                retMsg["Unmatched"] = unmatchedByPlex
                runningState = 0
                statusMsg = 'done'
            except ValueError:
                Log.Info('Aborted in ScanMedias')
            except Exception, e:
                Log.Exception('Exception happend in scanMedias: ' + str(e))
                statusMsg = wtV3().GETTRANSLATE(self, None, Internal=True, String='Idle')

        # ************ Main function ************
        Log.Debug('scanSection started')
        try:
            del mediasFromDB[:]										# Files from the database
            del mediasFromFileSystem[:]						# Files from the file system
            # Grap the section number from the req
            try:
                sectionNumber = args[0][0]
            except:
                Log.Critical('Missing section key')
                req.clear()
                req.set_status(412)
                req.finish('Missing section parameter')
            # Let's find out the info of section here
            response = XML.ElementFromURL(self.CoreUrl).xpath(
                '//Directory[@key=' + sectionNumber + ']')
            sectionTitle = response[0].get('title')
            sectionType = response[0].get('type')
            locations = response[0].xpath(
                '//Directory[@key=' + sectionNumber + ']/Location')
            sectionLocations = []
            for location in locations:
                sectionLocations.append(os.path.normpath(location.get('path')))
            Log.Debug('Going to scan section %s with a title of %s and a type of %s and locations as %s' % (
                sectionNumber, sectionTitle, sectionType, str(sectionLocations)))
            if runningState in [0, 99]:
                Thread.Create(scanMedias, globalize=True, sectionNumber=sectionNumber,
                              sectionLocations=sectionLocations, sectionType=sectionType, req=req)
            else:
                req.clear()
                req.set_status(409)
                req.finish('Scanning already in progress')
        except Exception, ex:
            Log.Exception('Fatal error happened in scanSection: ' + str(ex))
            req.clear()
            req.set_status(500)
            req.finish('Fatal error happened in scanSection: ' + str(ex))
            return req

    # Abort
    @classmethod
    def ABORT(self, req, *args):
        global runningState
        runningState = 0
        global bAbort
        bAbort = True
        req.clear()
        req.set_status(200)

    # Get supported Section list
    @classmethod
    def GETSECTIONSLIST(self, req, *args):
        Log.Debug('getSectionsList requested')
        try:
            rawSections = XML.ElementFromURL(
                misc.GetLoopBack() + '/library/sections')
            Sections = []
            for directory in rawSections:
                if directory.get('type') in SUPPORTEDSECTIONS:
                    Section = {'key': directory.get('key'), 'title': directory.get(
                        'title'), 'type': directory.get('type')}
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

    # Return the result
    @classmethod
    def GETRESULT(self, req, *args):
        # Are we in idle mode?
        if runningState == 0:
            req.clear()
            if 'WebTools' in retMsg:
                req.set_status(204)
            else:
                Log.Info('Result is: ' + str(retMsg))
                req.set_status(200)
                req.set_header(
                    'Content-Type', 'application/json; charset=utf-8')
                req.finish(retMsg)
        elif runningState == 99:
            if bAbort:
                req.set_status(204)
            else:
                req.set_status(204)
        else:
            req.clear()
            req.set_status(204)
        return

    # Return current status
    @classmethod
    def GETSTATUS(self, req, *args):
        req.clear()
        req.set_status(200)
        if runningState == 0:
            req.finish('Idle')
        else:
            req.finish(statusMsg)

    # Reset settings to default
    @classmethod
    def RESETSETTINGS(self, req, *args):
        Dict['findMedia'] = None
        Dict.Save()
        self.populatePrefs()
        req.clear()
        req.set_status(200)

    # Return the settings of this plugin
    @classmethod
    def GETSETTINGS(self, req, *args):
        req.clear()
        req.set_header('Content-Type', 'application/json; charset=utf-8')
        req.set_status(200)
        req.finish(json.dumps(Dict['findMedia']))

################### Internal functions #############################

    ''' Get the relevant function and call it with optinal params '''
    @classmethod
    def getFunction(self, metode, req, *args):
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

    ''' Populate the defaults, if not already there '''
    @classmethod
    def populatePrefs(self):
        try:
            if Dict['findMedia'] == None:
                Dict['findMedia'] = {
                    'IGNORE_HIDDEN': True,
                    'IGNORED_DIRS': [".@__thumb", ".AppleDouble", "lost+found"],
                    'VALID_EXTENSIONS': VALIDEXT['video'],
                    'IGNORE_EXTRAS': True,
                    'IGNORE_SPECIALS': True
                }
                Dict.Save()
            # New key from V3.0, so need to handle seperately
            if 'IGNORE_EXTRAS' not in Dict['findMedia'].keys():
                Dict['findMedia']['IGNORE_EXTRAS'] = True
                Dict.Save()
            # New key from V3.0, so need to handle seperately
            if 'IGNORE_SPECIALS' not in Dict['findMedia'].keys():
                Dict['findMedia']['IGNORE_SPECIALS'] = True
                Dict.Save()
        except Exception, e:
            Log.Exception('Exception in populatePrefs was %s' % str(e))

    '''
    Returns true or false, depending on if a media should be added to the list
    Param file: The file to be investigated, with full path
    Param mediaType: Type of media
    '''
    @classmethod
    def addThisItem(self, file, mediaType):
        try:
            if os.path.splitext(file)[1].lower()[1:] in Dict['findMedia']['VALID_EXTENSIONS']:
                parts = self.splitall(file)
                for part in parts:
                    if Dict['findMedia']['IGNORE_EXTRAS']:
                        if part.lower() in ExtrasDirs:
                            return False
                        for extra in Extras:
                            if extra in part.lower():
                                return False
                    # Ignore specials
                    if Dict['findMedia']['IGNORE_SPECIALS']:
                        for special in Specials:
                            if special == part.lower():
                                return False
                    # Ignore hiddens
                    if Dict['findMedia']['IGNORE_HIDDEN']:
                        if part.startswith('.'):
                            return False
                return True
            else:
                return False
        except Exception, e:
            Log.Exception('Exception in addThisItem was %s' % str(e))
            return False

    ''' Returns the different parts of a filepath '''
    @classmethod
    def splitall(self, path):
        allparts = []
        while 1:
            parts = os.path.split(path)
            if parts[0] == path:  # sentinel for absolute paths
                allparts.insert(0, parts[0])
                break
            elif parts[1] == path:  # sentinel for relative paths
                allparts.insert(0, parts[1])
                break
            else:
                path = parts[0]
                allparts.insert(0, parts[1])
        return allparts
