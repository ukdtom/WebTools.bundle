######################################################################################################################
#	pms helper unit
# A WebTools bundle plugin
#
#	Author: dane22, a Plex Community member
#
######################################################################################################################
from consts import NAME
from misc import misc
import shutil
import os
import time
import json
import io
import sys
from xml.etree import ElementTree

GET = ['SEARCH', 'GETALLBUNDLEINFO', 'GETSECTIONSLIST', 'GETSECTIONSIZE', 'GETSECTIONLETTERLIST', 'GETSECTION', 'GETSUBTITLES',
       'GETPARTS', 'SHOWSUBTITLE', 'GETSHOWSIZE', 'GETSHOWSEASONS', 'GETSHOWSEASON', 'GETSHOWCONTENTS', 'DOWNLOADSUBTITLE']
PUT = ['']
POST = ['UPLOADFILE', 'UPLOADSUB']
DELETE = ['DELBUNDLE', 'DELSUB']


class pmsV3(object):
    # Defaults used by the rest of the class
    @classmethod
    def init(self):
        self.PLUGIN_DIR = Core.storage.join_path(
            Core.app_support_path, Core.config.bundles_dir_name)

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

    ''' Download Subtitle '''
    @classmethod
    def DOWNLOADSUBTITLE(self, req, *args):
        Log.Debug('Download Subtitle requested')
        try:
            # Get the key of the sub
            try:
                key = args[0][0]
            except Exception, e:
                Log.Debug(
                    'Exception in downloadSubtitle when fetching the key was: ' + str(e))
                req.clear()
                req.set_status(412)
                req.finish('Missing key of subtitle')
                return req
            Log.Debug('Subtitle key is %s' % (key))
            myURL = misc.GetLoopBack() + '/library/streams/' + key
            try:
                # Grab the subtitle
                try:
                    response = HTML.StringFromElement(
                        HTML.ElementFromURL(myURL))
                except Exception, e:
                    Log.Exception(
                        'Fatal error happened in downloadSubtitle: ' + str(e))
                    req.clear()
                    req.set_status(404)
                    req.finish(
                        'Fatal error happened in downloadSubtitle: ' + str(e))
                # Make it more nice
                response = response.replace('<p>', '', 1)
                response = response.replace('</p>', '', 1)
                response = response.replace('&gt;', '>')
                response = response.split('\n')
                # Prep the download http headers
                req.set_header('Content-Disposition',
                               'attachment; filename="subtitle.srt"')
                req.set_header('Cache-Control', 'no-cache')
                req.set_header('Pragma', 'no-cache')
                req.set_header('Content-Type', 'application/text/plain')
                # Download the sub
                try:
                    for line in response:
                        req.write(line + '\n')
                    req.finish()
                    return req
                except Exception, e:
                    Log.Exception(
                        'Fatal error happened in downloadSubtitle: ' + str(e))
                    req.clear()
                    req.set_status(500)
                    req.finish(
                        'Fatal error happened in downloadSubtitle: ' + str(e))
            except Exception, e:
                Log.Exception(
                    'Fatal error happened in downloadSubtitle: %s' % (e))
                req.clear()
                req.set_status(500)
                req.finish('Fatal error happened in downloadSubtitle')
        except Exception, e:
            Log.Exception('Fatal error happened in downloadSubtitle: %s' % (e))
            req.clear()
            req.set_status(500)
            req.finish('Fatal error happened in downloadSubtitle')

    # Delete subtitle
    @classmethod
    def DELSUB(self, req, *args):
        Log.Debug('Delete subtitle requested')
        # TODO: Remove when #420 is done
        if Platform.OS == 'MacOSX':
            Log.Critical('MacOSX detected, so aborting')
            req.clear()
            req.set_status(405)
            req.finish(
                'Sadly not working on Mac OSx at the moment. Stay tuned for an update')
        try:
            # Start by checking if we got what it takes ;-)
            # Get params
            if not args:
                req.clear()
                req.set_status(412)
                req.finish('Missing params')
            params = args[0]
            try:
                key = params[params.index('key') + 1]
            except:
                req.clear()
                req.set_status(412)
                req.finish('Missing key')
            try:
                subKey = params[params.index('sub') + 1]
            except:
                req.clear()
                req.set_status(412)
                req.finish('Missing sub')
            myURL = misc.GetLoopBack() + '/library/metadata/' + key + '/tree'
            # Grap the sub
            sub = XML.ElementFromURL(myURL).xpath(
                '//MediaStream[@id=' + subKey + ']')
            if len(sub) > 0:
                # Sub did exists, but does it have an url?
                filePath = sub[0].get('url')
                if not filePath:
                    # Got an embedded sub here
                    Log.Debug(
                        'Fatal error happened in delSub, subtitle not found')
                    req.clear()
                    req.set_status(406)
                    req.finish(
                        'Hmmm....This is invalid, and most likely due to trying to delete an embedded sub :-)')
                else:
                    if filePath.startswith('media://'):
                        # Path to symblink
                        filePath = filePath.replace(
                            'media:/', os.path.join(Core.app_support_path, 'Media', 'localhost'))
                        try:
                            # Subtitle name
                            agent, sub = filePath.rsplit('_', 1)
                            tmp, agent = agent.split('com.')
                            # Agent used
                            agent = 'com.' + agent
                            filePath2 = filePath.replace('Contents', os.path.join(
                                'Contents', 'Subtitle Contributions'))
                            filePath2, language = filePath2.split('Subtitles')
                            language = language[1:3]
                            filePath3 = os.path.join(
                                filePath2[:-1], agent, language, sub)
                        except Exception, e:
                            Log.Exception(
                                'Exception in delSub generation file Path: ' + str(e))
                        subtitlesXMLPath, tmp = filePath.split('Contents')
                        agentXMLPath = os.path.join(
                            subtitlesXMLPath, 'Contents', 'Subtitle Contributions', agent + '.xml')
                        subtitlesXMLPath = os.path.join(
                            subtitlesXMLPath, 'Contents', 'Subtitles.xml')
                        self.DelFromXML(agentXMLPath, 'media', sub)
                        self.DelFromXML(subtitlesXMLPath, 'media', sub)
                        # Nuke the actual file
                        try:
                            # Delete the actual file
                            if os.path.exists(filePath):
                                os.remove(filePath)
                            # Delete the symb link
                            if os.path.exists(filePath3):
                                os.remove(filePath3)
                            # TODO: Refresh is sadly not working for me, so could use some help here :-(
                            # Let's refresh the media
                            url = misc.GetLoopBack() + '/library/metadata/' + key + '/refresh?force=1'
                            HTTP.Request(url, cacheTime=0,
                                         immediate=True, method="PUT")
                        except Exception, e:
                            Log.Exception(
                                'Exception while deleting an agent based sub: ' + str(e))
                            req.clear()
                            req.set_status(404)
                            req.finish(
                                'Exception while deleting an agent based sub: ' + str(e))
                        retValues = {}
                        retValues['FilePath'] = filePath3
                        retValues['SymbLink'] = filePath
                        Log.Debug('Agent subtitle returning %s' % (retValues))
                        req.clear()
                        req.set_status(200)
                        req.set_header(
                            'Content-Type', 'application/json; charset=utf-8')
                        req.finish(json.dumps(retValues))
                    elif filePath.startswith('file://'):
                        # We got a sidecar here, so killing time.....YES
                        filePath = filePath.replace('file://', '')
                        try:
                            # Delete the actual file
                            os.remove(filePath)
                            retVal = {}
                            retVal['Deleted file'] = filePath
                            Log.Debug('Deleted the sub %s' % (filePath))
                            req.clear()
                            req.set_status(200)
                            req.set_header(
                                'Content-Type', 'application/json; charset=utf-8')
                            req.finish(json.dumps(retVal))
                        except Exception, e:
                            # Could not find req. subtitle
                            Log.Exception(
                                'Fatal error happened in delSub, when deleting ' + filePath + ' : ' + str(e))
                            req.clear()
                            req.set_status(403)
                            req.finish('Fatal error happened in delSub, when deleting %s : %s' % (
                                filePath, str(e)))
            else:
                # Could not find req. subtitle
                Log.Debug('Fatal error happened in delSub, subtitle not found')
                req.clear()
                req.set_status(404)
                req.finish('Could not find req. subtitle')
        except Ex.HTTPError, e:
            req.clear()
            req.set_status(e.code)
            req.finish(str(e))
        except Exception, e:
            Log.Exception('Fatal error happened in delSub: ' + str(e))
            req.clear()
            req.set_status(500)
            req.finish('Fatal error happened in delSub: ' + str(e))

    # Get Contents
    @classmethod
    def GETSHOWCONTENTS(self, req, *args):
        try:
            # Get params
            if not args:
                req.clear()
                req.set_status(412)
                req.finish('Missing params')
            params = args[0]
            key = params[0]
            try:
                start = params[params.index('start') + 1]
            except Exception, e:
                req.clear()
                req.set_status(412)
                req.finish('Missing start in params')
            try:
                size = params[params.index('size') + 1]
            except Exception, e:
                req.clear()
                req.set_status(412)
                req.finish('Missing size in params')
            bGetSubs = ('getSubs' in params)
            myURL = misc.GetLoopBack() + '/library/metadata/' + key + \
                '/grandchildren?X-Plex-Container-Start=' + \
                start + '&X-Plex-Container-Size=' + size
            shows = XML.ElementFromURL(myURL).xpath('//Video')
            episodes = []
            for media in shows:
                episode = {}
                episode['key'] = media.get('ratingKey')
                episode['title'] = media.get('title')
                episode['season'] = media.get('parentIndex')
                episode['episode'] = media.get('index')
                if bGetSubs:
                    episode['subtitles'] = self.GETSUBTITLES(
                        req, mediaKey=episode['key'])
                episodes.append(episode)
            Log.Debug('Returning episodes as %s' % (episodes))
            req.clear()
            req.set_status(200)
            req.set_header('Content-Type', 'application/json; charset=utf-8')
            req.finish(json.dumps(episodes))
        except Exception, e:
            Log.Exception(
                'Fatal error happened in TV-Show while fetching contents %s' % (e))
            req.clear()
            req.set_status(500)
            req.finish(
                'Fatal error happened in TV-Show while fetching contents')

    # Get Season contents
    @classmethod
    def GETSHOWSEASON(self, req, *args):
        Log.Debug('GETSEASON requested')
        # Get params
        try:
            if not args:
                req.clear()
                req.set_status(412)
                req.finish('Missing params')
        except Exception, e:
            Log.Debug('Fatal error digesting params: ' + str(args[0]))
            req.clear()
            req.set_status(500)
            req.finish('Fatal error digesting params: ' + str(args[0]))
        Log.Debug('Argumets are: ' + str(args[0]))
        key = args[0][0]
        bGetSubs = ('getSub' in args[0])
        bGetFile = ('getFile' in args[0])
        try:
            myURL = misc.GetLoopBack() + '/library/metadata/' + key + '/tree'
            episodes = XML.ElementFromURL(myURL).xpath(
                './/MetadataItem/MetadataItem')
            mySeason = []
            for episode in episodes:
                myEpisode = {}
                myEpisode['key'] = episode.get('id')
                myEpisode['title'] = episode.get('title')
                myEpisode['episode'] = episode.get('index')
                if bGetSubs:
                    if bGetFile:
                        myEpisode['subtitles'] = self.GETSUBTITLES(
                            req, 'getFile', mediaKey=myEpisode['key'])
                    else:
                        myEpisode['subtitles'] = self.GETSUBTITLES(
                            req, mediaKey=myEpisode['key'])
                    if not Dict['HideWithoutSubs']:
                        mySeason.append(myEpisode)
                    else:
                        if len(myEpisode['subtitles']) > 0:
                            mySeason.append(myEpisode)
                else:
                    mySeason.append(myEpisode)
            Log.Debug('returning: %s' % (mySeason))
            req.clear()
            req.set_status(200)
            req.set_header('Content-Type', 'application/json; charset=utf-8')
            req.finish(json.dumps(mySeason))
        except Exception, e:
            Log.Exception(
                'Fatal error happened in TV-Show while fetching season: %s' % (e))
            req.clear()
            req.set_status(500)
            req.finish('Fatal error happened in TV-Show while fetching season')

    # Get Seasons list
    @classmethod
    def GETSHOWSEASONS(self, req, *args):
        Log.Debug('GETSHOWSEASONS requested')
        # Get params
        try:
            if not args:
                req.clear()
                req.set_status(412)
                req.finish('Missing params')
            key = args[0][0]
        except Exception, e:
            Log.Debug('Fatal error digesting params: ' + str(args[0]))
            req.clear()
            req.set_status(500)
            req.finish('Fatal error digesting params: ' + str(args[0]))
        Log.Debug('Key is: ' + key)
        try:
            myURL = misc.GetLoopBack() + '/library/metadata/' + key + '/children'
            mySeasons = []
            seasons = XML.ElementFromURL(myURL).xpath('//Directory')
            for season in seasons:
                if season.get('ratingKey'):
                    mySeason = {}
                    mySeason['title'] = season.get('title')
                    mySeason['key'] = season.get('ratingKey')
                    mySeason['season'] = season.get('index')
                    mySeason['size'] = season.get('leafCount')
                    mySeasons.append(mySeason)
            Log.Debug('Returning seasons as %s' % (mySeasons))
            req.clear()
            req.set_status(200)
            req.set_header('Content-Type', 'application/json; charset=utf-8')
            req.finish(str(json.dumps(mySeasons)))
        except Ex.HTTPError, e:
            req.clear()
            req.set_status(e.code)
            req.finish(str(e))
        except Exception, e:
            Log.Exception(
                'Fatal error happened in TV-Show while fetching seasons: %s' % (e))
            req.clear()
            req.set_status(500)
            req.finish(
                'Fatal error happened in TV-Show while fetching seasons: %s' % (e))

    # Get TVShow Size
    @classmethod
    def GETSHOWSIZE(self, req, *args):
        Log.Debug('GETSHOWSIZE requested')
        # Get params
        try:
            if not args:
                req.clear()
                req.set_status(412)
                req.finish('Missing params')
            key = args[0][0]
        except Exception, e:
            Log.Debug('Fatal error digesting params: ' + str(args[0]))
            req.clear()
            req.set_status(500)
            req.finish('Fatal error digesting params: ' + str(args[0]))
        Log.Debug('Key is: ' + key)
        # Grap TV-Show size
        myURL = misc.GetLoopBack() + '/library/metadata/' + key + \
            '/grandchildren?X-Plex-Container-Start=0&X-Plex-Container-Size=0'
        try:
            size = XML.ElementFromURL(myURL).get('totalSize')
            Log.Debug('Returning size as %s' % (size))
            req.clear()
            req.set_status(200)
            req.finish(size)
        except Ex.HTTPError, e:
            req.clear()
            req.set_status(e.code)
            req.finish(str(e))
        except:
            Log.Exception(
                'Fatal error happened in TV-Show while fetching size %s' % (e))
            req.clear()
            req.set_status(500)
            req.finish('Fatal error happened in TV-Show while fetching size')

    # Delete Bundle
    @classmethod
    def DELBUNDLE(self, req, *args):
        Log.Debug('Delete bundle requested')

        def removeBundle(bundleName, bundleIdentifier, url):
            try:
                bundleDataDir = Core.storage.join_path(
                    Core.app_support_path, 'Plug-in Support', 'Data', bundleIdentifier)
                bundleCacheDir = Core.storage.join_path(
                    Core.app_support_path, 'Plug-in Support', 'Caches', bundleIdentifier)
                bundlePrefsFile = Core.storage.join_path(
                    Core.app_support_path, 'Plug-in Support', 'Preferences', bundleIdentifier + '.xml')
                try:
                    # Find the bundle directory, regarding of the case used
                    dirs = os.listdir(self.PLUGIN_DIR)
                    for pluginDir in dirs:
                        if pluginDir.endswith('.bundle'):
                            # It's a bundle
                            if pluginDir.upper() == bundleName.upper():
                                bundleInstallDir = Core.storage.join_path(
                                    Core.app_support_path, Core.config.bundles_dir_name, pluginDir)
                    Log.Debug('Bundle directory name digested as: %s' %
                              (bundleInstallDir))
                    shutil.rmtree(bundleInstallDir)
                except Exception, e:
                    Log.Exception(
                        'Unable to remove the bundle directory: ' + str(e))
                    req.clear()
                    req.set_status(500)
                    req.finish(
                        'Fatal error happened when trying to remove the bundle directory: ' + str(e))
                try:
                    shutil.rmtree(bundleDataDir)
                except:
                    Log.Debug('Unable to remove the bundle data directory.')
                    Log.Debug(
                        'This can be caused by bundle data directory was never generated')
                    Log.Debug('Ignoring this')
                try:
                    shutil.rmtree(bundleCacheDir)
                except:
                    Log.Debug('Unable to remove the bundle cache directory.')
                    Log.Debug(
                        'This can be caused by bundle data directory was never generated')
                    Log.Debug('Ignoring this')
                try:
                    os.remove(bundlePrefsFile)
                except:
                    Log.Debug('Unable to remove the bundle preferences file.')
                    Log.Debug(
                        'This can be caused by bundle prefs was never generated')
                    Log.Debug('Ignoring this')
                # Remove entry from list dict
                Dict['installed'].pop(url, None)
                # remove entry from PMS-AllBundleInfo dict
                if url.startswith('https://'):
                    if 'Unknown' in Dict['PMS-AllBundleInfo'][url]['type']:
                        # Manual install or migrated, so nuke the entire key
                        Dict['PMS-AllBundleInfo'].pop(url, None)
                    else:
                        # UAS bundle, so only nuke date field
                        git = Dict['PMS-AllBundleInfo'][url]
                        git['date'] = ''
                        Dict['PMS-AllBundleInfo'][url] = git
                else:
                    # Manual install or migrated, so nuke the entire key
                    Dict['PMS-AllBundleInfo'].pop(url, None)
                Dict.Save()
                updateUASTypesCounters()
# TODO
                try:
                    Log.Debug(
                        'Reminder to self...TODO....Restart of System Bundle hangs :-(')
#					HTTP.Request('http://127.0.0.1:32400/:/plugins/com.plexapp.system/restart', immediate=True)
                except:
                    Log.Debug(
                        'Unable to restart System.bundle. Channel may not vanish without PMS restart.')
                    req.clear()
                    req.set_status(500)
                    req.finish(
                        'Fatal error happened when trying to restart the system.bundle')
            except Exception, e:
                Log.Exception(
                    'Fatal error happened in removeBundle: ' + str(e))
                req.clear()
                req.set_status(500)
                req.finish('Fatal error happened in removeBundle' + str(e))
        # Main function
        try:
            # Start by checking if we got what it takes ;-)
            try:
                if not args:
                    req.clear()
                    req.set_status(412)
                    req.finish('Missing params')
                params = args[0]
                bundleName = params[0]
            except Exception, e:
                Log.Debug('Fatal error digesting params: ' + str(params))
                req.clear()
                req.set_status(500)
                req.finish('Fatal error digesting params: ' + str(params))
            installedBundles = Dict['installed']
            bFoundBundle = False
            for installedBundle in installedBundles:
                if installedBundles[installedBundle]['bundle'].upper() == bundleName.upper():
                    removeBundle(
                        bundleName, installedBundles[installedBundle]['identifier'], installedBundle)
                    bFoundBundle = True
                    break
            if not bFoundBundle:
                Log.Debug('Bundle %s was not found' % (bundleName))
                req.clear()
                req.set_status(404)
                req.finish('Bundle %s was not found' % (bundleName))
            Log.Debug('Bundle %s was removed' % (bundleName))
            req.clear()
            req.set_status(200)
            req.finish('Bundle %s was removed' % (bundleName))
        except Exception, e:
            Log.Exception('Fatal error happened in delBundle: %s' % (e))
            req.clear()
            req.set_status(500)
            req.finish('Fatal error happened in delBundle')

    ''' Show Subtitle '''
    @classmethod
    def SHOWSUBTITLE(self, req, *args):
        Log.Debug('Show Subtitle requested')
        try:
            try:
                if not args:
                    req.clear()
                    req.set_status(412)
                    req.finish('Missing params')
                params = args[0]
                key = params[0]
            except Exception, e:
                Log.Debug('Fatal error digesting params: ' + str(params))
                req.clear()
                req.set_status(500)
                req.finish('Fatal error digesting params: ' + str(params))
            Log.Debug('Subtitle key is %s' % (key))
            myURL = misc.GetLoopBack() + '/library/streams/' + key
            try:
                response = HTML.StringFromElement(HTML.ElementFromURL(myURL))
                response = response.replace('<p>', '', 1)
                response = response.replace('</p>', '', 1)
                response = response.replace('&gt;', '>')
                response = response.split('\n')
                req.clear()
                req.set_status(200)
                req.set_header(
                    'Content-Type', 'application/json; charset=utf-8')
                req.finish(json.dumps(response))
            except Ex.HTTPError, e:
                req.clear()
                req.set_status(e.code)
                req.finish(str(e))
            except Exception, e:
                Log.Exception('Fatal error happened in showSubtitle: %s' % (e))
                req.clear()
                req.set_status(500)
                req.finish('Fatal error happened in showSubtitle')
        except Exception, e:
            Log.Exception('Fatal error happened in showSubtitle: %s' % (e))
            req.clear()
            req.set_status(500)
            req.finish('Fatal error happened in showSubtitle')

    # getParts
    @classmethod
    def GETPARTS(self, req, *args):
        Log.Debug('Got a call for getParts')
        try:
            # Get params
            try:
                if not args:
                    req.clear()
                    req.set_status(412)
                    req.finish('Missing params')
                params = args[0]
                key = params[0]
            except Exception, e:
                Log.Debug('Fatal error digesting params: ' + str(params))
                req.clear()
                req.set_status(500)
                req.finish('Fatal error digesting params: ' + str(params))
            try:
                partsUrl = misc.GetLoopBack() + '/library/metadata/' + key
                partsInfo = {}
                parts = XML.ElementFromURL(partsUrl).xpath('//Part')
                for part in parts:
                    partsInfo[part.get('id')] = part.get('file')
                # Not found
                if not partsInfo:
                    Log.Debug('getParts didnt find parts for key: ' + key)
                    req.clear()
                    req.set_status(404)
                    req.finish('getParts didnt find parts for key: ' + key)
                else:
                    Log.Debug('Returning: ' + json.dumps(partsInfo))
                    req.set_status(200)
                    req.set_header(
                        'Content-Type', 'application/json; charset=utf-8')
                    req.finish(json.dumps(partsInfo))
            except Ex.HTTPError, e:
                self.clear()
                self.set_status(e.code)
                self.finish(str(e))
            except Exception, e:
                Log.Debug(str(e))
                self.clear()
                self.set_status(500)
                self.finish(str(e))
        except Exception, e:
            Log.Exception('Fatal error happened in getParts: ' + str(e))
            req.clear()
            req.set_status(500)
            req.finish('Fatal error happened in getParts: ' + str(e))

    ''' get Subtitles '''
    @classmethod
    def GETSUBTITLES(self, req, *args, **kwargs):
        Log.Debug('Subtitles requested')
        try:
            getFile = False
            # Get params
            try:
                if not args:
                    if 'mediaKey' not in kwargs:
                        req.clear()
                        req.set_status(412)
                        req.finish('Missing params')
                else:
                    params = args[0]
                    getFile = ('getFile' in params)
                if 'mediaKey' in kwargs:
                    key = kwargs['mediaKey']
                else:
                    key = params[0]
            except Exception, e:
                Log.Debug('Fatal error digesting params: ' + str(params))
                req.clear()
                req.set_status(500)
                req.finish('Fatal error digesting params: ' + str(params))
            # Path to media
            myURL = misc.GetLoopBack() + '/library/metadata/' + key
            mediaInfo = []
            try:
                bDoGetTree = True
                # Only grap subtitle here
                streams = XML.ElementFromURL(myURL).xpath(
                    '//Stream[@streamType="3"]')
                for stream in streams:
                    subInfo = {}
                    subInfo['key'] = stream.get('id')
                    subInfo['codec'] = stream.get('codec')
                    subInfo['selected'] = stream.get('selected')
                    subInfo['languageCode'] = stream.get('languageCode')
                    if stream.get('key') == None:
                        location = 'Embedded'
                    elif stream.get('format') == None:
                        location = 'Agent'
                    else:
                        location = 'Sidecar'
                    subInfo['location'] = location
                    # Get tree info, if not already done so, and if it's a none embedded srt, and we asked for all
                    if getFile == True:
                        if location != None:
                            if bDoGetTree:
                                MediaStreams = XML.ElementFromURL(
                                    myURL + '/tree').xpath('//MediaStream')
                                bDoGetTree = False
                    if getFile == True:
                        try:
                            for mediaStream in MediaStreams:
                                if mediaStream.get('id') == subInfo['key']:
                                    subInfo['url'] = mediaStream.get('url')
                        except Exception, e:
                            Log.Exception(
                                'Fatal error happened in getSubtitles: %s' % (e))
                            req.clear()
                            req.set_status(500)
                            req.finish('Fatal error happened in getSubtitles')
                    mediaInfo.append(subInfo)
            except Exception, e:
                Log.Exception('Fatal error happened in getSubtitles %s' % (e))
                req.clear()
                req.set_status(500)
                req.finish('Fatal error happened in getSubtitles')
            # Internal call?
            if 'mediaKey' in kwargs:
                return mediaInfo
            else:
                # Nope, external call, so return http response
                req.clear()
                req.set_status(200)
                req.set_header(
                    'Content-Type', 'application/json; charset=utf-8')
                req.finish(json.dumps(mediaInfo))
        except Exception, e:
            Log.Exception('Fatal error happened in getSubtitles: %s' % (e))
            req.clear()
            req.set_status(500)
            req.finish('Fatal error happened in getSubtitles')

    ''' get section '''
    @classmethod
    def GETSECTION(self, req, *args):
        Log.Debug('Section requested')
        # Get params
        try:
            if not args:
                req.clear()
                req.set_status(412)
                req.finish('Missing params')
            params = args[0]
            try:
                start = params[params.index('start') + 1]
            except Exception, e:
                req.clear()
                req.set_status(412)
                req.finish('Missing start in params')
            try:
                size = params[params.index('size') + 1]
            except Exception, e:
                req.clear()
                req.set_status(412)
                req.finish('Missing size in params')
            try:
                key = params[params.index('key') + 1]
            except Exception, e:
                req.clear()
                req.set_status(412)
                req.finish('Missing key in params')
            getSubs = ('getSubs' in params)
            try:
                letterKey = params[params.index('letterKey') + 1].upper()
            except Exception, e:
                letterKey = None
            try:
                title = params[params.index('title') + 1].upper()
            except Exception, e:
                title = None
            # Got all the needed params, so lets grap the contents
            try:
                if letterKey and title:
                    myURL = misc.GetLoopBack() + '/library/sections/' + key + '/firstCharacter/' + \
                        letterKey + '?X-Plex-Container-Start=' + \
                        start + '&X-Plex-Container-Size=' + size + '&title=' + title
                elif letterKey:
                    myURL = misc.GetLoopBack() + '/library/sections/' + key + '/firstCharacter/' + \
                        letterKey + '?X-Plex-Container-Start=' + \
                        start + '&X-Plex-Container-Size=' + size
                elif title:
                    myURL = misc.GetLoopBack() + '/library/sections/' + key + '/all?X-Plex-Container-Start=' + \
                        start + '&X-Plex-Container-Size=' + size + '&title=' + title
                else:
                    myURL = misc.GetLoopBack() + '/library/sections/' + key + \
                        '/all?X-Plex-Container-Start=' + start + '&X-Plex-Container-Size=' + size
                rawSection = XML.ElementFromURL(myURL)
                Section = []
                for media in rawSection:
                    if getSubs == True:
                        subtitles = self.GETSUBTITLES(
                            req, mediaKey=media.get('ratingKey'))
                        if str(Dict['HideWithoutSubs']).lower() == 'true':
                            if len(subtitles) > 0:
                                # Found subs
                                media = {'key': media.get('ratingKey'), 'title': media.get(
                                    'title'), 'subtitles': subtitles}
                            else:
                                continue
                        else:
                            # Add regardless of subs present or not
                            media = {'key': media.get('ratingKey'), 'title': media.get(
                                'title'), 'subtitles': subtitles}
                    else:
                        media = {'key': media.get(
                            'ratingKey'), 'title': media.get('title')}
                    Section.append(media)
                Log.Debug('Returning %s' % (Section))
                req.clear()
                req.set_status(200)
                req.set_header(
                    'Content-Type', 'application/json; charset=utf-8')
                req.finish(json.dumps(
                    {'Section': Section, 'count': len(rawSection)}))
            except Exception, e:
                Log.Exception(
                    'Fatal error happened in getSection %s' % (str(e)))
                req.clear()
                req.set_status(500)
                req.finish('Fatal error happened in getSection')
        except Exception, e:
            Log.Exception('Fatal error happened in getSection: %s' % (str(e)))
            req.clear()
            req.set_status(500)
            req.finish('Fatal error happened in getSection')

    ''' get section letter-list '''
    @classmethod
    def GETSECTIONLETTERLIST(self, req, *args):
        Log.Debug('Section requested')
        try:
            if not args:
                req.clear()
                req.set_status(412)
                req.finish('Missing key of section')
            else:
                key = list(args)[0][0]
                # Got all the needed params, so lets grap the list
                myURL = misc.GetLoopBack() + '/library/sections/' + key + '/firstCharacter'
                resultJson = {}
                sectionLetterList = XML.ElementFromURL(
                    myURL).xpath('//Directory')
                for sectionLetter in sectionLetterList:
                    resultJson[sectionLetter.get('title')] = {
                        'key': sectionLetter.get('key'), 'size': sectionLetter.get('size')}
                Log.Debug('Returning %s' % (resultJson))
                req.clear()
                req.set_status(200)
                req.set_header(
                    'Content-Type', 'application/json; charset=utf-8')
                req.finish(json.dumps(resultJson, sort_keys=True))
        except Ex.HTTPError, e:
            req.clear()
            req.set_status(e.code)
            req.finish(str(e))
        except Exception, e:
            Log.Exception(
                'Fatal error happened in getSectionLetterList: %s ' % (str(e)))
            req.clear()
            req.set_status(500)
            req.finish(
                'Fatal error happened in getSectionLetterList: ' + str(e))

    ''' Get a section size '''
    @classmethod
    def GETSECTIONSIZE(self, req, *args):
        Log.Debug('Retrieve Section size')
        try:
            if not args:
                req.clear()
                req.set_status(412)
                req.finish('Missing key of section')
            else:
                key = list(args)[0][0]

                myURL = misc.GetLoopBack() + '/library/sections/' + key + \
                    '/all?X-Plex-Container-Start=0&X-Plex-Container-Size=0'
                try:
                    section = XML.ElementFromURL(myURL)
                    Log.Debug('Returning size as %s' %
                              (section.get('totalSize')))
                    req.clear()
                    req.set_status(200)
                    req.finish(section.get('totalSize'))
                except Ex.HTTPError, e:
                    Log.Debug('Error happened in GetSectionSize: %s' %
                              (str(e)))
                    req.clear()
                    req.set_status(e.code)
                    req.finish(
                        'Fatal error happened in GetSectionSize:  %s' % (str(e)))
                except Exception, e:
                    Log.Exception(
                        'Fatal error happened in GetSectionSize: %s' % (str(e)))
                    req.clear()
                    req.set_status(500)
                    req.finish(
                        'Fatal error happened in GetSectionSize:  %s' % (str(e)))
        except Exception, e:
            Log.Exception(
                'Fatal error happened in getSectionSize: %s' % (str(e)))
            req.clear()
            req.set_status(500)
            req.finish('Fatal error happened in getSectionSize')

    ''' get sections list '''
    @classmethod
    def GETSECTIONSLIST(self, req, *args):
        Log.Debug('getSectionsList requested')
        try:
            rawSections = XML.ElementFromURL(
                misc.GetLoopBack() + '/library/sections')
            Sections = []
            for directory in rawSections:
                Section = {'key': directory.get('key'), 'title': directory.get(
                    'title'), 'type': directory.get('type')}
                Sections.append(Section)
            Log.Debug('Returning Sectionlist as %s' % (Sections))
            try:
                params = args[0]
                # Got a filter ?
                for param in params:
                    if param.startswith('filter?'):
                        filter = param
                result = misc.filterJson(json.dumps(Sections), filter)
            except Exception, e:
                result = Sections
                pass
            req.clear()
            req.set_status(200)
            req.set_header('Content-Type', 'application/json; charset=utf-8')
            req.finish(json.dumps(result))
        except Exception, e:
            Log.Exception(
                'Fatal error happened in getSectionsList: %s' % (str(e)))
            req.clear()
            req.set_status(500)
            req.finish('Fatal error happened in getSectionsList')

    # getAllBundleInfo
    @classmethod
    def GETALLBUNDLEINFO(self, req, *args):
        Log.Debug('Got a call for getAllBundleInfo')
        try:
            req.clear()
            Log.Debug('Returning: ' +
                      str(len(Dict['PMS-AllBundleInfo'])) + ' items')
            req.set_status(200)
            req.set_header('Content-Type', 'application/json; charset=utf-8')
            retArray = []
            for key, value in Dict['PMS-AllBundleInfo'].items():
                d = {}
                d[key] = value
                retArray.append(d)
            Log.Debug('Returning: ' +
                      str(len(Dict['PMS-AllBundleInfo'])) + ' items')
            req.finish(json.dumps(retArray))
        except Exception, e:
            Log.Exception(
                'Fatal error happened in getAllBundleInfo: ' + str(e))
            req.clear()
            req.set_status(500)
            req.finish('Fatal error happened in getAllBundleInfo: ' + str(e))

    ''' uploadFile Takes remoteFile and localFile (Type file) as params '''
    @classmethod
    def UPLOADFILE(self, req, *args):
        Log.Debug('Got a call for uploadFile')
        try:
            # Target filename present?
            remoteFile = req.get_argument('remoteFile', 'missing')
            if remoteFile == 'missing':
                req.clear()
                req.set_status(412)
                req.finish('Missing remoteFile parameter')
            # Upload file present?
            if not 'localFile' in req.request.files:
                req.clear()
                req.set_status(412)
                req.finish('Missing upload file parameter named localFile')
            else:
                # Grap the upload file
                localFile = req.request.files['localFile'][0]
                # Save it
                output_file = io.open(remoteFile, 'wb')
                output_file.write(localFile['body'])
                output_file.close
                req.clear()
                req.set_status(200)
                req.finish('Upload ok')
        except Exception, e:
            Log.Exception('Fatal error happened in uploadFile: ' + str(e))
            req.clear()
            req.set_status(500)
            req.finish('Fatal error happened in uploadFile: ' + str(e))

    ''' uploadFile Takes remoteFile and localFile (Type file) as params '''
    @classmethod
    def UPLOADSUB(self, req, *args):
        Log.Debug('Got a call for uploadSUB')
        try:
            # Get the Language code
            language = req.get_argument('language', default=None, strip=False)
            if language == None:
                req.clear()
                req.set_status(412)
                req.finish('Missing language param from the payload')
            # Make sure we have a media key
            if len(args) > 0:
                # Arguments present
                if 'key' in args[0]:
                    try:
                        key = args[0][args[0].index('key') + 1]
                    except:
                        req.clear()
                        req.set_status(412)
                        req.finish('Missing media key value parameter')
                    try:
                        part = args[0][args[0].index('part') + 1]
                    except:
                        req.clear()
                        req.set_status(412)
                        req.finish('Missing media part value parameter')
            # Upload file present?
            if not 'localFile' in req.request.files:
                req.clear()
                req.set_status(412)
                req.finish(
                    'Missing upload file parameter named localFile from the payload')
            else:
                localFile = req.request.files['localFile'][0]
                # Lookup media
                url = misc.GetLoopBack() + '/library/metadata/' + key + \
                    '?excludeElements=Actor,Collection,Country,Director,Genre,Label,Mood,Producer,Similar,Writer,Role'
                media = XML.ElementFromURL(url)
                mediaFile = media.xpath(
                    '//Part[@id=' + part + ']')[0].get('file')
                remoteFile = os.path.splitext(
                    mediaFile)[0] + '.' + language + '.srt'
                # Save it
                output_file = io.open(remoteFile, 'wb')
                output_file.write(localFile['body'])
                output_file.close
                req.clear()
                req.set_status(200)
                req.finish('Upload ok')
        except Exception, e:
            Log.Exception('Fatal error happened in uploadSub: ' + str(e))
            req.clear()
            req.set_status(500)
            req.finish('Fatal error happened in uploadSub: ' + str(e))

    ''' Search for a title '''
    @classmethod
    def SEARCH(self, req, *args):
        Log.Info('Search called')
        try:
            try:
                searchTitle = args[0][0]
            except Exception, e:
                Log.Debug('Exception here due to missing search title')
                req.set_status(412)
                req.finish('No title to search for?')
            url = misc.GetLoopBack() + '/search?query=' + searchTitle
            result = {}
            # Fetch search result from PMS
            foundMedias = XML.ElementFromURL(url)
            # Grap all movies from the result
            for media in foundMedias.xpath('//Video'):
                value = {}
                value['title'] = media.get('title')
                value['type'] = media.get('type')
                value['section'] = media.get('librarySectionID')
                key = media.get('ratingKey')
                result[key] = value
            # Grap results for TV-Shows
            for media in foundMedias.xpath('//Directory'):
                value = {}
                value['title'] = media.get('title')
                value['type'] = media.get('type')
                value['section'] = media.get('librarySectionID')
                key = media.get('ratingKey')
                result[key] = value
            Log.Info('Search returned: %s' % (result))
            req.clear()
            req.set_status(200)
            req.set_header('Content-Type', 'application/json; charset=utf-8')
            req.finish(json.dumps(result))
        except Exception, e:
            Log.Exception('Fatal error happened in search: ' + str(e))
            req.clear()
            req.set_status(500)
            req.finish('Fatal error happened in search: ' + str(e))

#************************************* Internal function *********************************************

    ''' Delete from an XML file Internal class function'''
    @classmethod
    def DelFromXML(self, fileName, attribute, value):
        Log.Debug('Need to delete element with an attribute named "%s" with a value of "%s" from file named "%s"' % (
            attribute, value, fileName))
        if Platform.OS == 'MacOSX':
            Log.Info('Mac OSx detected')
            try:
                xmlFile = os.fdopen(os.open(fileName, os.O_RDWR), "r+")
                with xmlFile as f:
                    tree = ElementTree.parse(f)
                    root = tree.getroot()
                    mySubtitles = root.findall('.//Subtitle')
                    for Subtitles in root.findall("Language[Subtitle]"):
                        for node in Subtitles.findall("Subtitle"):
                            myValue = node.attrib.get(attribute)
                            if myValue:
                                if '_' in myValue:
                                    drop, myValue = myValue.split("_")
                                if myValue == value:
                                    Subtitles.remove(node)
                    tree.write(f, encoding='utf-8', xml_declaration=True)
            except Exception, e:
                Log.Exception('Exception in DelFromXML was %s' % e)
        else:
            Log.Info('Non Mac OSx detected')
            with io.open(fileName, 'r') as f:
                tree = ElementTree.parse(f)
                root = tree.getroot()
                mySubtitles = root.findall('.//Subtitle')
                for Subtitles in root.findall("Language[Subtitle]"):
                    for node in Subtitles.findall("Subtitle"):
                        myValue = node.attrib.get(attribute)
                        if myValue:
                            if '_' in myValue:
                                drop, myValue = myValue.split("_")
                            if myValue == value:
                                Subtitles.remove(node)
            tree.write(fileName, encoding='utf-8', xml_declaration=True)
        return


##################################### Below need to be converted to API V3 ##########################################################


################ Functions exposed to other modules #####################

# Undate uasTypesCounters
def updateUASTypesCounters():
    try:
        alliCounter = 0
        alltCounter = 0
        counter = {}
        # Grap a list of all bundles
        bundleList = Dict['PMS-AllBundleInfo']
        for bundle in bundleList:
            for bundleType in bundleList[bundle]['type']:
                if bundleType in counter:
                    tCounter = int(counter[bundleType]['total'])
                    tCounter += 1
                    alltCounter += 1
                    iCounter = int(counter[bundleType]['installed'])
                    if 'date' not in bundleList[bundle]:
                        bundleList[bundle]['date'] = ''
                    if bundleList[bundle]['date'] != '':
                        iCounter += 1
                        alliCounter += 1
                    counter[bundleType] = {
                        'installed': iCounter, 'total': tCounter}
                else:
                    if 'date' not in bundleList[bundle]:
                        counter[bundleType] = {'installed': 0, 'total': 1}
                    elif bundleList[bundle]['date'] == '':
                        counter[bundleType] = {'installed': 0, 'total': 1}
                    else:
                        counter[bundleType] = {'installed': 1, 'total': 1}
                    alltCounter += 1
        counter['All'] = {'installed': alliCounter, 'total': alltCounter}
        Dict['uasTypes'] = counter
        Dict.Save()
    except Exception, e:
        Log.Exception(
            'Fatal error happened in updateUASTypesCounters: ' + str(e))

# TODO fix updateAllBundleInfo
# updateAllBundleInfo


def updateAllBundleInfoFromUAS():
    def updateInstallDict():
        # Start by creating a fast lookup cache for all uas bundles
        uasBundles = {}
        bundles = Dict['PMS-AllBundleInfo']
        for bundle in bundles:
            uasBundles[bundles[bundle]['identifier']] = bundle
        # Now walk the installed ones
        try:
            installed = Dict['installed'].copy()
            for installedBundle in installed:
                if not installedBundle.startswith('https://'):
                    Log.Info('Checking unknown bundle: ' +
                             installedBundle + ' to see if it is part of UAS now')
                    if installedBundle in uasBundles:
                        # Get the installed date of the bundle formerly known as unknown :-)
                        installedBranch = Dict['installed'][installedBundle]['branch']
                        installedDate = Dict['installed'][installedBundle]['date']
                        # Add updated stuff to the dicts
                        Dict['PMS-AllBundleInfo'][uasBundles[installedBundle]
                                                  ]['branch'] = installedBranch
                        Dict['PMS-AllBundleInfo'][uasBundles[installedBundle]
                                                  ]['date'] = installedDate
                        Dict['installed'][uasBundles[installedBundle]
                                          ] = Dict['PMS-AllBundleInfo'][uasBundles[installedBundle]]
                        # Remove old stuff from the Dict
                        Dict['PMS-AllBundleInfo'].pop(installedBundle, None)
                        Dict['installed'].pop(installedBundle, None)
                        Dict.Save()
        except Exception, e:
            Log.Exception(
                'Critical error in updateInstallDict while walking the gits: ' + str(e))
        return
    try:
        # start by checking if UAS cache has been populated
        if Data.Exists('plugin_details.json'):
            Log.Debug('UAS was present')
            # Let's open it, and walk the gits one by one
            # Convert to a JSON Object
            gits = Data.LoadObject('plugin_details.json')
            try:
                for git in gits:
                    # Rearrange data
                    key = git['repo']
                    installBranch = ''
                    # Check if already present, and if an install date also is there
                    installDate = ""
                    CommitId = ""
                    if key in Dict['PMS-AllBundleInfo']:
                        jsonPMSAllBundleInfo = Dict['PMS-AllBundleInfo'][key]
                        if 'date' in jsonPMSAllBundleInfo:
                            installDate = Dict['PMS-AllBundleInfo'][key]['date']
                        if 'CommitId' in jsonPMSAllBundleInfo:
                            CommitId = Dict['PMS-AllBundleInfo'][key]['CommitId']
                    del git['repo']
                    # Add/Update our Dict
                    Dict['PMS-AllBundleInfo'][key] = git
                    Dict['PMS-AllBundleInfo'][key]['date'] = installDate
                    Dict['PMS-AllBundleInfo'][key]['CommitId'] = CommitId
            except Exception, e:
                Log.Exception(
                    'Critical error in updateAllBundleInfoFromUAS1 while walking the gits: ' + str(e))
            Dict.Save()
            updateUASTypesCounters()
            updateInstallDict()
        else:
            Log.Debug('UAS was sadly not present')
    except Exception, e:
        Log.Exception(
            'Fatal error happened in updateAllBundleInfoFromUAS: ' + str(e))
