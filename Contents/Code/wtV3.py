######################################################################################################################
#	WT unit
# A WebTools bundle plugin
#
# Used for internal functions to WebTools
#
#	Author: dane22, a Plex Community member
#
######################################################################################################################

import glob
import json
import shutil
import sys
import os
import io
from consts import BUNDLEDIRNAME, NAME, VERSION, WT_URL
from plextvhelper import plexTV
from shutil import copyfile
from misc import misc

GET = ['GETCSS', 'GETUSERS', 'GETLANGUAGELIST',
       'GETTRANSLATORLIST', 'GETCURRENTLANG']
PUT = ['RESET', 'UPGRADEWT']
POST = ['UPDATELANGUAGE', 'GETTRANSLATE']
DELETE = ['']

PAYLOAD = 'aWQ9MTE5Mjk1JmFwaV90b2tlbj0wODA2OGU0ZjRkNTI3NDVlOTM0NzAyMWQ2NDU5MGYzOQ__'
TRANSLATESITEBASE = 'https://api.poeditor.com/v2'
TRANSLATESITEHEADER = {'content-type': 'application/x-www-form-urlencoded'}


class wtV3(object):

    @classmethod
    def init(self):
        return

    #********** Functions below ******************

    ''' Get the language code for the UI '''
    @classmethod
    def GETCURRENTLANG(self, req, *args, **kwargs):
        if kwargs:
            if kwargs['Internal']:
                return Dict['UILanguage']
            else:
                Log.Error(
                    'WT.getCurrentLang was called with kwargs, but no internal was set')
        else:
            req.clear()
            req.set_status(200)
            req.set_header('Content-Type', 'application/json; charset=utf-8')
            lang = {}
            lang['Language'] = Dict['UILanguage']
            req.finish(json.dumps(lang))

    ''' Upgrade WebTools from latest release. This is the new call, that replace the one that in V2 was located in the git module '''
    @classmethod
    def UPGRADEWT(self, req, *args):
        Log.Info('We recieved a call to upgrade WebTools itself')
        upgradeURL = WT_URL.replace(
            'https://github.com/', 'https://api.github.com/repos/') + '/releases/latest'
        Log.Info('Release URL on Github is %s' % upgradeURL)
        try:
            downloadUrl = None
            # Digest release info, in order to grab the download url
            jsonReponse = JSON.ObjectFromURL(upgradeURL)
            # Walk assets to find the one named WebTools.bundle.zip
            for asset in jsonReponse['assets']:
                if asset['name'] == 'WebTools.bundle.zip':
                    downloadUrl = asset['browser_download_url']
                    break
            Log.Info('Downloading %s' % downloadUrl)
            # Grap file from Github
            zipfile = Archive.ZipFromURL(downloadUrl)
            for filename in zipfile:
                realFileName = filename.replace(NAME + '.bundle', '')
                if realFileName.startswith('/'):
                    realFileName = realFileName[1:]
                saveFileName = Core.storage.join_path(
                    Core.bundle_path + '.upgrade', realFileName)
                if saveFileName.endswith('/'):
                    continue
                else:
                    Log.Debug('Extracting file %s' % saveFileName)
                    try:
                        Core.storage.ensure_dirs(os.path.dirname(saveFileName))
                        Core.storage.save(saveFileName, zipfile[filename])
                    except Exception, e:
                        bError = True
                        Log.Exception(
                            'Exception happend in UPGRADEWT: ' + str(e))
            # All done, so now time to flip directories
            try:
                os.rename(Core.bundle_path, Core.storage.join_path(
                    Core.bundle_path.replace(NAME + '.bundle', ''), NAME + '.bundle.upgraded'))
                os.rename(Core.storage.join_path(Core.bundle_path.replace(
                    NAME + '.bundle', ''), NAME + '.bundle.upgrade'), Core.bundle_path)
            except Exception, e:
                Log.Exception(
                    'Exception in UPGRADEWT during rename was %s' % str(e))
        except Exception, e:
            Log.Exception('Exception in UPGRADEWT was %s' % str(e))
            req.clear()
            if e.code == 200:
                req.set_status(500)
            else:
                req.set_status(e.code)
            req.finish(str(e))
            return
        req.clear()
        req.set_status(200)
        req.finish('WebTools finished upgrading')

    ''' Get list of translators '''
    @classmethod
    def GETTRANSLATORLIST(self, req, *args):
        try:
            response = HTTP.Request(method='POST', url=TRANSLATESITEBASE + '/contributors/list',
                                    data=String.Decode(PAYLOAD), headers=TRANSLATESITEHEADER)
            jsonResponse = JSON.ObjectFromString(
                str(response))['result']['contributors']
            translators = {}
            for translator in jsonResponse:
                try:
                    translators[translator['name']
                                ] = translator['permissions'][0]['languages']
                except:
                    # Just skip if no lang avail, since it could be an admin
                    pass
            Log.Info('Returning: %s' % str(translators))
            req.set_status(200)
            req.set_header('Content-Type', 'application/json; charset=utf-8')
            req.finish(json.dumps(translators))
        except Exception, e:
            Log.Exception(
                'Exception happened in getTranslatorList was: ' + str(e))
            req.clear()
            req.set_status(e.code)
            req.finish(
                'Fatal error happened in wt.getTranslatorList: %s' % (str(e)))

    ''' Get list of avail languages, as well as their translation status '''
    @classmethod
    def GETLANGUAGELIST(self, req, *args):
        try:
            response = HTTP.Request(method='POST', url=TRANSLATESITEBASE + '/languages/list',
                                    data=String.Decode(PAYLOAD), headers=TRANSLATESITEHEADER)
            jsonResponse = JSON.ObjectFromString(str(response))
            req.set_status(200)
            req.set_header('Content-Type', 'application/json; charset=utf-8')
            req.finish(json.dumps(jsonResponse['result']['languages']))
        except Exception, e:
            Log.Exception(
                'Exception happened in getLanguageList was: ' + str(e))
            req.clear()
            req.set_status(e.code)
            req.finish(
                'Fatal error happened in wt.getLanguageList: %s' % (str(e)))

    ''' Get a translation string '''
    @classmethod
    def GETTRANSLATE(self, req, *args, **kwargs):
        try:
            Internal = False
            if kwargs:
                if kwargs['Internal']:
                    Internal = True
                    if kwargs['String']:
                        String = kwargs['String']
                        lang = self.GETCURRENTLANG(self, None, Internal=True)
                    else:
                        Log.Error(
                            'WT.getTranslate was called internally, but missed the string to translate')
                else:
                    Log.Error(
                        'WT.getTranslate was called with kwargs, but no internal was set')
            else:
                # Get the Payload
                data = json.loads(req.request.body.decode('utf-8'))
                if 'language' in data:
                    lang = data['language']
                else:
                    lang = self.GETCURRENTLANG(self, None, Internal=True)
                String = data['string']
            # If not having translations copied to DATA already, do so now
            if not Data.Exists('translations.js'):
                upgradeCleanup()
            try:
                # Now open existing translations.js file, walk it line by line, and find the correct line
                translationLines = Data.Load('translations.js').splitlines()
                transLine = None
                for line in translationLines:
                    # Got the relevant language?
                    if line.lstrip().startswith("gettextCatalog.setStrings('" + lang + "',"):
                        transLine = line
                        break
                if transLine:
                    jsonTransLine = JSON.ObjectFromString(
                        transLine.split(',', 1)[1].lstrip()[:-2])
                    if String in jsonTransLine:
                        if Internal:
                            return jsonTransLine[String]
                        else:
                            req.clear()
                            req.set_status(200)
                            req.finish(jsonTransLine[String])
                    else:
                        if Internal:
                            return String
                        else:
                            req.clear()
                            req.set_status(200)
                            req.finish(String)
                else:
                    if Internal:
                        return json.dumps(jsonTransLine)
                    else:
                        req.clear()
                        req.set_status(200)
                        req.set_header(
                            'Content-Type', 'application/json; charset=utf-8')
                        req.finish(json.dumps(jsonTransLine))

            except Exception, e:
                Log.Exception(
                    'Exception happened digesting the body was %s' % str(e))
                req.clear()
                req.set_status(e.code)
                req.finish(
                    'Exception happened digesting the body was %s' % str(e))
        except Exception, e:
            Log.Exception('Exception happened in getTranslate was: ' + str(e))
            req.clear()
            req.set_status(e.code)
            req.finish('Fatal error happened in wt.getTranslate: %s' %
                       (str(e)))

    ''' Download and update a translation from live translation site '''
    @classmethod
    def UPDATELANGUAGE(self, req, *args):
        try:
            # Get params
            if not args:
                req.clear()
                req.set_status(412)
                req.finish('Missing params')
            params = args[0]
            # Get the language param
            try:
                lang = params[params.index('lang') + 1]
                # Get list of valid languages
                languages = {}
                jsonLanguages = getTranslationLanguages()[
                    'result']['languages']
                for item in jsonLanguages:
                    languages[item['code']] = item['name']
                # Unsupported language?
                if lang not in languages:
                    Log.Error('Unsupported language %s' % lang)
                    req.clear()
                    req.set_status(412)
                    req.finish('Unsupported lang')
                # Get download link
                try:
                    payLoad = String.Decode(
                        PAYLOAD) + '&language=' + lang + '&type=key_value_json'
                    response = HTTP.Request(method='POST', url=TRANSLATESITEBASE +
                                            '/projects/export', data=payLoad, headers=TRANSLATESITEHEADER)
                    url = JSON.ObjectFromString(str(response))['result']['url']
                    # Download updated translation file, and minimize it
                    translated = json.dumps(JSON.ObjectFromURL(
                        url=url), separators=(',', ':'))
                    # Now open existing translations.js file, walk it line by line, and update the relevant translation
                    translationLines = Data.Load(
                        'translations.js').splitlines()
                    bFound = False
                    translatedStr = ''
                    for line in translationLines:
                        # Got the relevant language?
                        if line.lstrip().startswith("gettextCatalog.setStrings('" + lang + "',"):
                            start = line.split(',', 1)[0]
                            translatedStr = translatedStr + '\n' + start + ',' + translated + ');'
                            bFound = True
                        else:
                            if translatedStr == '':
                                translatedStr = line
                            else:
                                translatedStr = translatedStr + '\n' + line
                    # New not yet seen language?
                    if not bFound:
                        translatedStr = translatedStr[:-23] + "    gettextCatalog.setStrings('" + lang + "'," + translated + ');\n' + translatedStr[len(
                            translatedStr) - 23:]
                    # Save the updated translation file
                    Data.Save('translations.js', translatedStr)
                    # Update Plugin translation files as well
                    createPluginStringTranslations()
                except Exception, e:
                    Log.Exception(
                        'Exception happened in updateLanguage while fetching download link was: ' + str(e))
                    req.clear()
                    req.set_status(e.code)
                    req.finish(
                        'Fatal error happened in wt.updateLanguage while fetching download link was: %s' % (str(e)))
            except:
                Log.Error('Unsupported lang')
                req.clear()
                req.set_status(412)
                req.finish('Missing lang')
        except Exception, e:
            Log.Exception(
                'Exception happened in updateLanguage was: ' + str(e))
            req.clear()
            req.set_status(e.code)
            req.finish(
                'Fatal error happened in wt.updateLanguage: %s' % (str(e)))

    ''' Get list of users '''
    @classmethod
    def GETUSERS(self, req, *args):
        try:
            users = plexTV().getUserList()
            req.clear()
            if users == None:
                Log.Error('Access denied towards plex.tv')
                req.set_status(401)
            else:
                req.set_status(200)
                req.set_header(
                    'Content-Type', 'application/json; charset=utf-8')
                req.finish(json.dumps(users))
        except Exception, e:
            Log.Exception('Fatal error happened in wt.getUsers: ' + str(e))
            req.clear()
            req.set_status(e.code)
            req.finish('Fatal error happened in wt.getUsers: %s' % (str(e)))

    '''  Reset WT to factory settings '''
    @classmethod
    def RESET(self, req, *args):
        try:
            Log.Info('Factory Reset called')
            cachePath = Core.storage.join_path(
                Core.app_support_path, 'Plug-in Support', 'Caches', 'com.plexapp.plugins.' + NAME)
            dataPath = Core.storage.join_path(
                Core.app_support_path, 'Plug-in Support', 'Data', 'com.plexapp.plugins.' + NAME)
            shutil.rmtree(cachePath)
            shutil.rmtree(dataPath)
            try:
                Dict.Reset()
            except:
                Log.Critical('Fatal error in clearing dict during reset')
            # Restart system bundle
            HTTP.Request(misc.GetLoopBack() + '/:/plugins/com.plexapp.plugins.' +
                         NAME + '/restart', cacheTime=0, immediate=True)
            req.clear()
            req.set_status(200)
            req.finish('WebTools has been reset')
        except Exception, e:
            Log.Exception('Fatal error happened in wt.reset: ' + str(e))
            req.clear()
            req.set_status(e.code)
            req.finish('Fatal error happened in wt.reset: %s' % (str(e)))

    ''' Get a list of all css files in http/custom_themes '''
    @classmethod
    def GETCSS(self, req, *args):
        Log.Debug('getCSS requested')
        try:
            targetDir = Core.storage.join_path(
                Core.app_support_path, Core.config.bundles_dir_name, BUNDLEDIRNAME, 'http', 'custom_themes')
            myList = glob.glob(targetDir + '/*.css')
            if len(myList) == 0:
                req.clear()
                req.set_status(204)
            else:
                for n, item in enumerate(myList):
                    myList[n] = item.replace(targetDir, '')
                    myList[n] = myList[n][1:]
                Log.Debug('Returning %s' % (myList))
                req.clear()
                req.set_status(200)
                req.set_header(
                    'Content-Type', 'application/json; charset=utf-8')
                req.finish(json.dumps(myList))
        except Exception, e:
            Log.Exception('Fatal error happened in getCSS: ' + str(e))
            req.clear()
            req.set_status(e.code)
            req.finish('Fatal error happened in getCSS: ' + str(e))

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


''' ********************* Internal functions *********************************** '''


''' This function will do a cleanup of old stuff, if needed '''


def upgradeCleanup():
    ''' Always check translation file regardless of version '''
    updateTranslationStore()
    ''' Remove leftovers from an upgrade '''
    removeUpgraded()
    '''
	We do take precedence here in a max of 3 integer digits in the version number !
	'''
    Log.Info('Running upgradeCleanup')
    versionArray = VERSION.split('.')
    try:
        major = int(versionArray[0])
    except Exception, e:
        Log.Exception(
            'Exception happened digesting the major number of the Version was %s' % (str(e)))
    try:
        minor = int(versionArray[1])
    except Exception, e:
        Log.Exception(
            'Exception happened digesting the minor number of the Version was %s' % (str(e)))
    try:
        ''' When getting rev number, we need to filter out stuff like dev version '''
        rev = int(versionArray[2].split(' ')[0])
    except Exception, e:
        Log.Exception(
            'Exception happened digesting the rev number of the Version was %s' % (str(e)))
    ''' Older than V3 ? '''
    if major > 2:
        ''' We need to delete the old uas dir, if present '''
        dirUAS = Core.storage.join_path(
            Core.app_support_path, Core.config.bundles_dir_name, NAME + '.bundle', 'http', 'uas')
        try:
            if os.path.isdir(dirUAS):
                Log.Debug('Found old uas V2 cache dir, so deleting that')
                shutil.rmtree(dirUAS)
        except Exception, e:
            Log.Exception(
                'We encountered an error during cleanup that was %s' % (str(e)))
            pass


''' Remove old version that's upgraded, if present '''


def removeUpgraded():
    try:
        pluginDir = Core.storage.join_path(
            Core.app_support_path, Core.config.bundles_dir_name, NAME + '.bundle.upgraded')
        if os.path.isdir(pluginDir):
            shutil.rmtree(pluginDir)
            Log.Info('Removed old upgraded WT from directory: %s' % pluginDir)
    except Exception, e:
        Log.Exception('Exception in removeUpgraded was %s' % str(e))


''' This function will update the translation.js file in PMS storage if needed '''


def updateTranslationStore():
    Log.Debug('updateTranslationStore started')
    bundleStore = Core.storage.join_path(
        Core.bundle_path, 'http', 'static', '_shared', 'translations.js')
    Log.Debug('bundleStore: %s' % bundleStore)
    dataStore = Core.storage.join_path(Core.app_support_path, 'Plug-in Support',
                                       'Data', 'com.plexapp.plugins.WebTools', 'DataItems', 'translations.js')
    Log.Debug('dataStore: %s' % dataStore)
    # If translations.js file already present in the store, we need to find out if it's newer or not
    if Data.Exists('translations.js'):
        try:
            # File exsisted, so let's compare datetime stamps
            dataStore_modified_time = os.stat(dataStore).st_mtime
            bundleStore_modified_time = os.stat(bundleStore).st_mtime
            if dataStore_modified_time < bundleStore_modified_time:
                Log.Info('Updating translation file in storage')
                copyfile(bundleStore, dataStore)
                createPluginStringTranslations()
        except Exception, e:
            Log.Exception(
                'Exception in updateTranslationStore was %s' % str(e))
    else:
        Log.Info('Updating translation file in storage')
        copyfile(bundleStore, dataStore)
        createPluginStringTranslations()
    return


''' Get a list of languages avail from translation site '''


def getTranslationLanguages():
    try:
        response = HTTP.Request(method='POST', url=TRANSLATESITEBASE + '/languages/list',
                                data=String.Decode(PAYLOAD), headers=TRANSLATESITEHEADER)
        jsonResponse = JSON.ObjectFromString(str(response))
        return jsonResponse
    except Exception, e:
        Log.Exception(
            'Exception happened in getTranslationLanguages was: ' + str(e))
        return None


''' Extraxt channel plugin translations from the translations.js file '''


def createPluginStringTranslations():
    try:
        # Get Strings directory
        STRINGSDIR = Core.storage.join_path(
            Core.bundle_path, 'Contents', 'Strings')
        # Now open existing translations.js file, walk it line by line, and update the relevant translation
        translationLines = Data.Load(
            'translations.js').splitlines()
        for line in translationLines:
            # Start of a language?
            if line.lstrip().startswith("gettextCatalog.setStrings('"):
                lang, translation = line.split("',", 1)
                # Grap language in Spe
                lang = lang.split("'")[1]
                # Temp store for translation file
                jsonTranslation = {}
                translation = translation[:-2]
                translationJson = JSON.ObjectFromString(translation)
                # Walk the translation for keys, looking for <PLUGIN>
                for key in translationJson:
                    if key.startswith('<plugin>'):
                        if translationJson[key][8:-9].replace('\n        ', ' ') != "":
                            jsonTranslation[key[8:-9].replace('\n        ', ' ')] = translationJson[key][8:-
                                                                                                         9].replace('\n        ', ' ')
                if len(jsonTranslation) > 0:
                    fileName = Core.storage.join_path(
                        STRINGSDIR, lang + '.json')
                    Core.storage.ensure_dirs(os.path.dirname(fileName))
                    with io.open(fileName, 'w', encoding="utf-8") as outfile:
                        outfile.write(
                            unicode(json.dumps(jsonTranslation, indent=4, ensure_ascii=False)))
    except Exception, e:
        Log.Exception(
            'Exception in createPluginStringTranslations was: %s' % str(e))
    return
