#!/usr/bin/env python
# -*- coding: utf-8 -*-
##############################################################################
# WebTools module unit
#
# Author: dane22, a Plex Community member
#
# This module is for constants used by WebTools and it's modules, as well as
# to control developer mode
#
# For info about the debug file, see the docs
###############################################################################

import io
import os
import json
import inspect
from random import randint  # Used for Cookie generation

# default for debug mode
DEBUGMODE = False
# validate password
WT_AUTH = True
# version of plugin
VERSION = 'ERROR'
# USA2 Repo branch
UAS_URL = 'https://github.com/ukdtom/UAS2Res'
# UAS2 branch to check
UAS_BRANCH = 'master'
# Prefix
PREFIX = ''
# Name of plugin
NAME = ''
# Name of Icon in Resource Dir
ICON = 'WebTools.png'
# Base url if behind a proxy
BASEURL = ''
# timestamp for json export
JSONTIMESTAMP = 0
# URL to latest WebTools
WT_URL = 'https://github.com/ukdtom/WebTools.bundle'
# Name of the bundle dir
BUNDLEDIRNAME = ''
# Elements to be excluded, when sending req. to PMS
EXCLUDEELEMENTS = ''.join((
                'excludeElements=Actor,',
                'Collection,Country,Director,',
                'Genre,Label,Mood,Producer,',
                'Similar,Writer,Role'))
EXCLUDEFIELDS = 'excludeFields=summary,tagline,file'
# Log Directory
LOG_DIR = ''

# Modules used in WebTools
V3MODULES = {
    'WT': 'wtV3', 'PMS': 'pmsV3', 'LOGS': 'logsV3',
    'LANGUAGE': 'languageV3', 'SETTINGS': 'settingsV3',
    'GIT': 'gitV3', 'FINDMEDIA': 'findMediaV3',
    'JSONEXPORTER': 'jsonExporterV3', 'PLAYLISTS': 'playlistsV3',
    'TECHINFO': 'techinfo', 'VIEWSTATE': 'viewstate',
    'CHANGEAGENT': 'changeagent'}
UILANGUAGE = 'en'
UILANGUAGEDEBUG = False

MEDIATYPE = {
            'Movie': 1, 'Show': 2, 'Season': 3, 'Episode': 4, 'Trailer': 5,
            'Comic': 6, 'Person': 7, 'Artist': 8, 'Album': 9, 'Track': 10,
            'Clip': 12, 'Photo': 13, 'Photo_Album': 14, 'Playlist': 15,
            'Playlist_Folder': 16, 'Podcast': 17
            }

VALIDEXT = {
    'video': [
            '3g2', '3gp', 'asf', 'asx', 'avc', 'avi', 'avs', 'bivx', 'bup',
            'divx', 'dv', 'dvr-ms', 'evo', 'fli', 'flv', 'm2t', 'm2ts',
            'm2v', 'm4v', 'mkv', 'mov', 'mp4', 'mpeg', 'mpg', 'mts', 'nsv',
            'nuv', 'ogm', 'ogv', 'tp', 'pva', 'qt', 'rm', 'rmvb', 'sdp',
            'svq3', 'strm', 'ts', 'ty', 'vdr', 'viv', 'vob', 'vp3', 'wmv',
            'wpl', 'wtv', 'xsp', 'xvid', 'webm'],
    'photo': [
            'png', 'jpg', 'jpeg', 'bmp', 'gif', 'ico', 'tif', 'tiff', 'tga',
            'pcx', 'dng', 'nef', ' cr2', 'crw', 'orf', 'arw', 'erf', '3fr',
            'dcr', 'x3f', 'mef', 'raf', 'mrw', 'pef', 'sr2', 'mpo', 'jps',
            'rw2', 'jp2', 'j2k'],
    'audio': [
            'mp3', 'm4a', 'm4b', 'flac', 'aac', 'rm', 'rma', 'mpa', 'wav',
            'wma', 'ogg', 'mp2', 'mka', 'ac3', 'dts', 'ape', 'mpc', 'mp+',
            'mpp', 'shn', 'oga', 'aiff', 'aif', 'wv', 'dsf', 'dsd', 'opus']
            }

PLEX_MEDIATYPE = {
    'METADATA_MOVIE': 1,
    'METADATA_SHOW': 2,
    'METADATA_SEASON': 3,
    'METADATA_EPISODE': 4,
    'METADATA_TRAILER': 5,
    'METADATA_COMIC': 6,
    'METADATA_PERSON': 7,
    'METADATA_ARTIST': 8,
    'METADATA_ALBUM': 9,
    'METADATA_TRACK': 10,
    'METADATA_CLIP': 12,
    'METADATA_PHOTO': 13,
    'METADATA_PHOTO_ALBUM': 14,
    'METADATA_PLAYLIST': 15,
    'METADATA_PLAYLIST_FOLDER': 16,
    'METADATA_PODCAST': 17
    }

ISO639_3 = {
        "Unknown": "unk",
        "Afar": "aar",
        "Abkhazian": "abk",
        "Afrikaans": "afr",
        "Akan": "aka",
        "Albanian": "alb",
        "Amharic": "amh",
        "Arabic": "ara",
        "Aragonese": "arg",
        "Armenian": "arm",
        "Assamese": "asm",
        "Avaric": "ava",
        "Avestan": "ave",
        "Aymara": "aym",
        "Azerbaijani": "aze",
        "Bashkir": "bak",
        "Bambara": "bam",
        "Basque": "baq",
        "Belarusian": "bel",
        "Bengali": "ben",
        "Bihari": "bih",
        "Bislama": "bis",
        "Bosnian": "bos",
        "Breton": "bre",
        "Bulgarian": "bul",
        "Burmese": "bur",
        "Catalan": "cat",
        "Chamorro": "cha",
        "Chechen": "che",
        "Chinese": "chi",
        "ChurchSlavic": "chu",
        "Chuvash": "chv",
        "Cornish": "cor",
        "Corsican": "cos",
        "Cree": "cre",
        "Czech": "cze",
        "Danish": "dan",
        "Divehi": "div",
        "Dutch": "dut",
        "Dzongkha": "dzo",
        "English": "eng",
        "Esperanto": "epo",
        "Estonian": "est",
        "Ewe": "ewe",
        "Faroese": "fao",
        "Fijian": "fij",
        "Finnish": "fin",
        "French": "fre",
        "Frisian": "fry",
        "Fulah": "ful",
        "Georgian": "geo",
        "German": "ger",
        "Gaelic": "gla",
        "Irish": "gle",
        "Galician": "glg",
        "Manx": "glv",
        "Greek": "ell",
        "Guarani": "grn",
        "Gujarati": "guj",
        "Haitian": "hat",
        "Hausa": "hau",
        "Hebrew": "heb",
        "Herero": "her",
        "Hindi": "hin",
        "HiriMotu": "hmo",
        "Croatian": "hrv",
        "Hungarian": "hun",
        "Igbo": "ibo",
        "Icelandic": "ice",
        "Ido": "ido",
        "SichuanYi": "iii",
        "Inuktitut": "iku",
        "Interlingue": "ile",
        "Interlingua": "ina",
        "Indonesian": "ind",
        "Inupiaq": "ipk",
        "Italian": "ita",
        "Javanese": "jav",
        "Japanese": "jpn",
        "Kalaallisut": "kal",
        "Kannada": "kan",
        "Kashmiri": "kas",
        "Kanuri": "kau",
        "Kazakh": "kaz",
        "Khmer": "khm",
        "Kikuyu": "kik",
        "Kinyarwanda": "kin",
        "Kirghiz": "kir",
        "Komi": "kom",
        "Kongo": "kon",
        "Korean": "kor",
        "Kuanyama": "kua",
        "Kurdish": "kur",
        "Lao": "lao",
        "Latin": "lat",
        "Latvian": "lav",
        "Limburgan": "lim",
        "Lingala": "lin",
        "Lithuanian": "lit",
        "Luxembourgish": "ltz",
        "LubaKatanga": "lub",
        "Ganda": "lug",
        "Macedonian": "mac",
        "Marshallese": "mah",
        "Malayalam": "mal",
        "Maori": "mao",
        "Marathi": "mar",
        "Malay": "may",
        "Malagasy": "mlg",
        "Maltese": "mlt",
        "Moldavian": "mol",
        "Mongolian": "mon",
        "Nauru": "nau",
        "Navajo": "nav",
        "SouthNdebele": "nbl",
        "NorthNdebele": "nde",
        "Ndonga": "ndo",
        "Nepali": "nep",
        "NorwegianNynorsk": "nno",
        "NorwegianBokmal": "nob",
        "Norwegian": "nor",
        "Chichewa": "nya",
        "Occitan": "oci",
        "Ojibwa": "oji",
        "Oriya": "ori",
        "Oromo": "orm",
        "Ossetian": "oss",
        "Panjabi": "pan",
        "Persian": "per",
        "Pali": "pli",
        "Polish": "pol",
        "Portuguese": "por",
        "Pushto": "pus",
        "Quechua": "que",
        "RaetoRomance": "roh",
        "Romanian": "rum",
        "Rundi": "run",
        "Russian": "rus",
        "Sango": "sag",
        "Sanskrit": "san",
        "Serbian": "scc",
        "Serbian": "srp",
        "Sinhalese": "sin",
        "Slovak": "slo",
        "Slovenian": "slv",
        "Sami": "sme",
        "Samoan": "smo",
        "Shona": "sna",
        "Sindhi": "snd",
        "Somali": "som",
        "Sotho": "sot",
        "Spanish": "spa",
        "Sardinian": "srd",
        "Swati": "ssw",
        "Sundanese": "sun",
        "Swahili": "swa",
        "Swedish": "swe",
        "Tahitian": "tah",
        "Tamil": "tam",
        "Tatar": "tat",
        "Telugu": "tel",
        "Tajik": "tgk",
        "Tagalog": "tgl",
        "Thai": "tha",
        "Tibetan": "tib",
        "Tigrinya": "tir",
        "Tonga": "ton",
        "Tswana": "tsn",
        "Tsonga": "tso",
        "Turkmen": "tuk",
        "Turkish": "tur",
        "Twi": "twi",
        "Uighur": "uig",
        "Ukrainian": "ukr",
        "Urdu": "urd",
        "Uzbek": "uzb",
        "Venda": "ven",
        "Vietnamese": "vie",
        "Volapuk": "vol",
        "Welsh": "wel",
        "Walloon": "wln",
        "Wolof": "wol",
        "Xhosa": "xho",
        "Yiddish": "yid",
        "Yoruba": "yor",
        "Zhuang": "zha",
        "Zulu": "zul",
        "Brazilian": "pob",
        "NoLanguage": "unk"
    }

EXCLUDEELEMENTS = ''.join((
                        'Actor,',
                        'Collection,',
                        'Country,',
                        'Director,',
                        'Genre,',
                        'Label,',
                        'Mood,',
                        'Producer,',
                        'Role,',
                        'Similar,',
                        'Writer'))

EXCLUDEFIELDS = 'summary,tagline'


class consts(object):
    init_already = False							# Make sure part of init only run once

    def setConsts(self):
        global DEBUGMODE
        global WT_AUTH
        global UAS_URL
        global UAS_BRANCH
        global VERSION
        global JSONTIMESTAMP
        global BUNDLEDIRNAME
        global NAME
        global PREFIX
        global BASEURL
        global UILANGUAGE
        global UILANGUAGEDEBUG
        global WT_URL
        global LOG_DIR

        # Lets find the name of the bundle directory
        BUNDLEDIRNAME = os.path.split(os.path.split(os.path.split(
            os.path.dirname(os.path.abspath(inspect.stack()[0][1])))[0])[0])[1]
        # Name of this plugin
        NAME = os.path.splitext(BUNDLEDIRNAME)[0]
        # Prefix
        PREFIX = '/applications/' + str(NAME).lower()
        if Prefs['Base_URL']:
            BASEURL = Prefs['Base_URL']
        if not BASEURL.startswith('/'):
            BASEURL = '/' + BASEURL
        if BASEURL.endswith('/'):
            BASEURL = BASEURL[:-1]
        # Grap version number from the version file
        try:
            versionFile = Core.storage.join_path(Core.bundle_path, 'VERSION')
            with io.open(versionFile, "rb") as version_file:
                VERSION = version_file.read().splitlines()[0]
        except:
            if not self.isCorrectPath():
                VERSION = '*** WRONG INSTALL PATH!!!!....Correct path is: ' + \
                    Core.storage.join_path(
                        Core.bundle_path, BUNDLEDIRNAME) + '***'
        # Switch to debug mode if needed
        debugFile = Core.storage.join_path(Core.bundle_path, 'debug')
        # Do we have a debug file ?
        if os.path.isfile(debugFile):
            DEBUGMODE = True
            VERSION = VERSION + ' ****** WARNING Debug mode on *********'
            try:
                # Read it for params
                json_file = io.open(debugFile, "rb")
                debug = json_file.read()
                json_file.close()
                debugParams = JSON.ObjectFromString(str(debug))
                Log.Debug('Override debug params are %s' % str(debugParams))
                if 'UAS_Repo' in debugParams:
                    UAS_URL = debugParams['UAS_Repo']
                if 'UAS_RepoBranch' in debugParams:
                    UAS_BRANCH = debugParams['UAS_RepoBranch']
                if 'WT_AUTH' in debugParams:
                    WT_AUTH = debugParams['WT_AUTH']
                if 'WT_URL' in debugParams:
                    WT_URL = debugParams['WT_URL']
                if 'JSONTIMESTAMP' in debugParams:
                    JSONTIMESTAMP = debugParams['JSONTIMESTAMP']
                # Try and fetch a user language, if set
                try:
                    UILANGUAGE = Dict['UILanguage']
                except:
                    pass
                # Running localization in debug mode?
                if 'UI' in debugParams:
                    if 'Language' in debugParams['UI']:
                        UILANGUAGE = debugParams['UI']['Language']
                    if 'debug' in debugParams['UI']:
                        UILANGUAGEDEBUG = (debugParams['UI']['debug'])
            except Exception, e:
                Log.Exception('Exception in const was %s' % (str(e)))
                pass
        else:
            DEBUGMODE = False
        try:
            if 'PLEX_MEDIA_SERVER_LOG_DIR' in os.environ:
                LOG_DIR = os.environ['PLEX_MEDIA_SERVER_LOG_DIR']
            elif ((sys.platform.find('linux') == 0) and (
                    'PLEXLOCALAPPDATA' in os.environ)):
                LOG_DIR = os.path.join(
                    os.environ['PLEXLOCALAPPDATA'],
                    'Plex Media Server',
                    'Logs')
            elif sys.platform == 'win32':
                if 'PLEXLOCALAPPDATA' in os.environ:
                    key = 'PLEXLOCALAPPDATA'
                else:
                    key = 'LOCALAPPDATA'
                LOG_DIR = os.path.join(
                    os.environ[key], 'Plex Media Server', 'Logs')
            else:
                LOG_DIR = os.path.join(
                    os.environ['HOME'], 'Library', 'Logs', 'Plex Media Server')
                if not os.path.isdir(LOG_DIR):
                    LOG_DIR = os.path.join(Core.app_support_path, 'Logs')
        except Exception, e:
            Log.Exception(
                'Fatal error happened in getting Log directory: %s' % e)
            req.clear()
            req.set_status(500)
            req.finish('Fatal error happened in Logs list: ' + str(e))
        Log.Debug('Log Root dir is: ' + LOG_DIR)

    ''' Init of the Class'''

    def __init__(self):
        self.makeDefaultSettings()
        self.setConsts()
        # Verify install path

        def isCorrectPath(self):
            try:
                installedPlugInPath = abspath(getsourcefile(
                    lambda: 0)).upper().split(BUNDLEDIRNAME, 1)[0]
                targetPath = Core.storage.join_path(
                    Core.app_support_path,
                    Core.config.bundles_dir_name).upper()
                if installedPlugInPath[:-1] != targetPath:
                    Log.Debug(
                        '************************************************')
                    Log.Debug('Wrong installation path detected!!!!')
                    Log.Debug('')
                    Log.Debug('Correct path is:')
                    Log.Debug(Core.storage.join_path(
                        Core.app_support_path,
                        Core.config.bundles_dir_name, BUNDLEDIRNAME))
                    Log.Debug(
                        '************************************************')
                    installedPlugInPath = abspath(
                        getsourcefile(lambda: 0)).split('/Contents', 1)[0]
                    return False
                else:
                    Log.Info(
                        'Verified a correct install path as: %s'
                        % (targetPath))
                    return True
            except Exception, e:
                Log.Exception('Exception in IsCorrectPath was: %s' % str(e))

    ''' This will generate the default settings in the Dict if missing '''
    def makeDefaultSettings(self):
        # Used for Cookie generation
        Dict['SharedSecret'] = VERSION + '.' + str(randint(0, 9999))
        # Set default value for http part, if run for the first time
        if Dict['options_hide_integrated'] is None:
            Dict['options_hide_integrated'] = 'false'
        # Set default value for http part, if run for the first time
        if Dict['options_hide_local'] is None:
            Dict['options_hide_local'] = 'false'
        # Set default value for http part, if run for the first time
        if Dict['options_hide_empty_subtitles'] is None:
            Dict['options_hide_empty_subtitles'] = 'false'
        # Set default value for http part, if run for the first time
        if Dict['options_only_multiple'] is None:
            Dict['options_only_multiple'] = 'false'
        # Set default value for http part, if run for the first time
        if Dict['options_auto_select_duplicate'] is None:
            Dict['options_auto_select_duplicate'] = 'false'
        # Set default value for http part, if run for the first time
        if Dict['items_per_page'] is None:
            Dict['items_per_page'] = '15'
        # Create the password entry
        if Dict['password'] is None:
            Dict['password'] = ''
        # Create the debug entry
        if Dict['debug'] is None:
            Dict['debug'] = 'false'
        # Create the pwdset entry
        if Dict['pwdset'] is None:
            Dict['pwdset'] = False
        # Init the installed dict
        if Dict['installed'] is None:
            Dict['installed'] = {}
        # Init the allBundle Dict
        if Dict['PMS-AllBundleInfo'] is None:
            Dict['PMS-AllBundleInfo'] = {}
        # Init the scheme used Dict
        if Dict['wt_csstheme'] is None:
            Dict['wt_csstheme'] = 'WhiteBlue.css'
        # Init default language to en, if none is present
        if Dict['UILanguage'] is None:
            Dict['UILanguage'] = 'en'
        # Init default language to en, if none is present
        if Dict['HideWithoutSubs'] is None:
            Dict['HideWithoutSubs'] = 'False'
        return


consts = consts()
