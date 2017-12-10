#!/usr/bin/env python
# -*- coding: utf-8 -*-
######################################################################################################################
#					WebTools bundle module for Plex
#
#					Allows you to extract some technical info about your Plex Media Server
#
#					Author:			dane22, a Plex Community member
#
#					Support thread:	http://forums.plex.tv/discussion/288191
#
######################################################################################################################

import sys
import locale
import os
import json
from wtV3 import wtV3
from misc import misc


GET = ['GETINFO']
PUT = []
POST = []
DELETE = []


class techinfo(object):
    @classmethod
    def init(self):
        return

    ''' Return technical info to the user '''
    @classmethod
    def GETINFO(self, req, *args):
        Log.Debug('Starting getInfo')
        try:
            techInfo = {}
            try:
                id = XML.ElementFromURL(misc.GetLoopBack() + '/identity')
            except:
                pass
            Log.Info(
                '************************** INFO from API **************************')
            try:
                Log.Info('OS is: ' + Platform.OS)
                techInfo['Platform'] = Platform.OS
            except:
                pass
            try:
                Log.Info('CPU is: ' + Platform.CPU)
                techInfo['CPU'] = Platform.CPU
            except:
                pass
            try:
                Log.Info('Python version is: ' + sys.version)
                techInfo['Python'] = sys.version
            except:
                pass
            try:
                Log.Info('Support Silverlight: ' + Platform.HasSilverlight)
                techInfo['Silverlight'] = Platform.HasSilverlight
            except:
                pass
            try:
                Log.Info('Locale is: ' + str(locale.getdefaultlocale()))
                techInfo['Locale'] = str(locale.getdefaultlocale())
            except:
                pass
            try:
                Log.Info('Machine Identifier: ' + id.get('machineIdentifier'))
                techInfo['MachineID'] = id.get('machineIdentifier')
            except:
                pass
            try:
                Log.Info('PMS Version: ' + id.get('version'))
                techInfo['PMSVersion'] = id.get('version')
            except:
                pass
            try:
                Log.Info('PMS App Support path: ' + Core.app_support_path)
                techInfo['AppSupportPath_FrameWork'] = Core.app_support_path
            except:
                pass
            Log.Info(
                '************************** INFO from ENV **************************')
            try:
                Log.Info('PLEX_MEDIA_SERVER_APPLICATION_SUPPORT_DIR: ' +
                         os.environ['PLEX_MEDIA_SERVER_APPLICATION_SUPPORT_DIR'])
                techInfo['AppSupportPath_OS'] = os.environ['PLEX_MEDIA_SERVER_APPLICATION_SUPPORT_DIR']
            except:
                pass
            try:
                Log.Info('PYTHONDONTWRITEBYTECODE: ' +
                         os.environ['PYTHONDONTWRITEBYTECODE'])
                techInfo['PythonDontWriteByteCode'] = os.environ['PYTHONDONTWRITEBYTECODE']
            except:
                pass
            try:
                Log.Info('USER: ' + os.environ['USER'])
                techInfo['User'] = os.environ['USER']
            except:
                pass
            try:
                Log.Info('HOME: ' + os.environ['HOME'])
                techInfo['Home'] = os.environ['HOME']
            except:
                pass
            try:
                Log.Info('LD_LIBRARY_PATH: ' + os.environ['LD_LIBRARY_PATH'])
                techInfo['LD_LIBRARY_PATH'] = os.environ['LD_LIBRARY_PATH']
            except:
                pass
            try:
                Log.Info('LANG: ' + os.environ['LANG'])
                techInfo['LANG'] = os.environ['LANG']
            except:
                pass
            try:
                Log.Info('LANGUAGE: ' + os.environ['LANGUAGE'])
                techInfo['LANGUAGE'] = os.environ['LANGUAGE']
            except:
                pass
            try:
                Log.Info('TMPDIR: ' + os.environ['TMPDIR'])
                techInfo['TMPDIR'] = os.environ['TMPDIR']
            except:
                pass
            try:
                Log.Info('PLEXLOCALAPPDATA: ' + os.environ['PLEXLOCALAPPDATA'])
                techInfo['PLEXLOCALAPPDATA'] = os.environ['PLEXLOCALAPPDATA']
            except:
                pass
            try:
                Log.Info('LC_ALL: ' + os.environ['LC_ALL'])
                techInfo['LC_ALL'] = os.environ['LC_ALL']
            except:
                pass
            try:
                Log.Info('Executable: ' + os.environ['_'])
                techInfo['Executable'] = os.environ['_']
            except:
                pass
            try:
                Log.Info('PLEXBUNDLEDEXTS: ' + os.environ['PLEXBUNDLEDEXTS'])
                techInfo['PLEXBUNDLEDEXTS'] = os.environ['PLEXBUNDLEDEXTS']
            except:
                pass
            try:
                Log.Info('PYTHONHOME: ' + os.environ['PYTHONHOME'])
                techInfo['PYTHONHOME'] = os.environ['PYTHONHOME']
            except:
                pass
            try:
                Log.Info('PWD: ' + os.environ['PWD'])
                techInfo['PWD'] = os.environ['PWD']
            except:
                pass
            try:
                Log.Info('PLEXBUNDLEDPLUGINSPATH: ' +
                         os.environ['PLEXBUNDLEDPLUGINSPATH'])
                techInfo['PLEXBUNDLEDPLUGINSPATH'] = os.environ['PLEXBUNDLEDPLUGINSPATH']
            except:
                pass
            try:
                Log.Info('PLEX_MEDIA_SERVER_MAX_PLUGIN_PROCS: ' +
                         os.environ['PLEX_MEDIA_SERVER_MAX_PLUGIN_PROCS'])
                techInfo['PLEX_MEDIA_SERVER_MAX_PLUGIN_PROCS'] = os.environ['PLEX_MEDIA_SERVER_MAX_PLUGIN_PROCS']
            except:
                pass
            try:
                Log.Info('PLEXTOKEN: **** SCRAMBLED ****')
                StringKey = 'PLEXTOKEN *********'
                StringValue = wtV3().GETTRANSLATE(None, None, Internal=True,
                                                  String='DO NOT SHARE THIS IN ANY PUBLIC WEBSITE!!!')
                techInfo[StringKey] = StringValue
                techInfo['PLEXTOKEN'] = os.environ['PLEXTOKEN']
            except:
                pass
            Log.Info('************************** INFO End **********************')
            try:
                if 'PLEX_MEDIA_SERVER_LOG_DIR' in os.environ:
                    LOGDIR = os.environ['PLEX_MEDIA_SERVER_LOG_DIR']
                elif sys.platform.find('linux') == 0 and 'PLEXLOCALAPPDATA' in os.environ:
                    LOGDIR = os.path.join(
                        os.environ['PLEXLOCALAPPDATA'], 'Plex Media Server', 'Logs')
                elif sys.platform == 'win32':
                    if 'PLEXLOCALAPPDATA' in os.environ:
                        key = 'PLEXLOCALAPPDATA'
                    else:
                        key = 'LOCALAPPDATA'
                    LOGDIR = os.path.join(
                        os.environ[key], 'Plex Media Server', 'Logs')
                else:
                    LOGDIR = os.path.join(
                        os.environ['HOME'], 'Library', 'Logs', 'Plex Media Server')
                    if not os.path.isdir(self.LOGDIR):
                        LOGDIR = os.path.join(Core.app_support_path, 'Logs')
            except Exception, e:
                Log.Exception(
                    'Fatal error happened in getting the Log Directory: ' + str(e))
                req.clear()
                req.set_status(500)
                req.finish(
                    'Fatal error happened in TechInfo getting the Log Dir list: ' + str(e))
            techInfo['Log Directory'] = LOGDIR
            req.clear()
            req.set_status(200)
            req.set_header(
                'Content-Type', 'application/json; charset=utf-8')
            req.finish(json.dumps(techInfo, sort_keys=True))
        except Exception, e:
            Log.Exception('Exception in getInfo: ' + str(e))
            req.clear()
            req.set_status(500)
            req.finish('Fatal error happened in getInfo: ' + str(e))
            return req

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
