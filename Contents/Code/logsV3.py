#!/usr/bin/env python
# -*- coding: utf-8 -*-
#############################################################################
# log files helper unit
# A WebTools bundle plugin
#
# Author: dane22, a Plex Community member
#
#############################################################################
import shutil
import time
import json
import os
import sys
import io
import zipfile
from consts import LOG_DIR

GET = ['LIST', 'SHOW', 'DOWNLOAD', 'LISTTIME']
PUT = ['ENTRY']
POST = []
DELETE = []


class logsV3(object):

    @classmethod
    def init(self):
        ''' Defaults used by the rest of the class '''
        self.LOGDIR = LOG_DIR

    @classmethod
    def getFunction(self, metode, req):
        ''' Get the relevant function and call it with optinal params '''
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

    # ********** Functions below ******************

    @classmethod
    def ENTRY(self, req, *args):
        '''
        This metode will add an entry to the logfile.
        Req param is: "text"
        '''
        Log.Debug('Starting Logs.entry function')
        try:
            try:
                # Get the Payload
                data = json.loads(req.request.body.decode('utf-8'))
            except Exception, e:
                req.set_status(412)
                req.finish('Not a valid payload?')
            if 'text' in data:
                Log.Debug('FrontEnd: ' + data['text'])
                req.clear()
                req.set_status(200)
                req.finish('Entry logged')
            else:
                req.set_status(404)
                req.finish('Missing text from payload?')
        except Exception, e:
            Log.Exception('Fatal error happened in Logs entry: ' + str(e))
            req.clear()
            req.set_status(500)
            req.finish('Fatal error happened in Logs entry: ' + str(e))

    @classmethod
    def DOWNLOAD(self, req, *args):
        '''
        This will download a zipfile with the complete log directory.
        if parameter fileName is specified, only that file will be
        downloaded, and not zipped
        '''
        try:
            self.init()
            if not args:
                fileName = ''
            else:
                fileName = list(args)[0][0]
            fileName = String.Unquote(fileName)
            Log.Debug(
                'About to download logs and \
                fileName param is: %s' % (fileName))
            if fileName == '':
                # Need to download entire log dir as a zip
                # Get current date and time, and add to filename
                downFile = 'PMSLogs_' + time.strftime("%Y%m%d-%H%M%S") + '.zip'
                zipFileName = 'PMSLogs.zip'
                myZip = zipfile.ZipFile(zipFileName, 'w')
                for root, dirs, files in os.walk(self.LOGDIR, topdown=True):
                    # Only zip from the default directories
                    dirs[:] = [d for d in dirs if d in ['PMS Plugin Logs']]
                    for filename in files:
                        fullFileName = os.path.join(root, filename)
                        param, value = fullFileName.split(self.LOGDIR, 1)
                        ext = os.path.splitext(filename)[1].upper()[1:]
                        if ((ext == 'LOG') or (ext.isdigit())):
                            myZip.write(os.path.join(
                                root, filename), arcname=value)
                myZip.close()
                req.set_header('Content-Disposition',
                               'attachment; filename="' + downFile + '"')
                req.set_header('Cache-Control', 'no-cache')
                req.set_header('Pragma', 'no-cache')
                req.set_header('Content-Type', 'application/zip')
                # with io.open(file, 'r', errors='ignore') as content_file:
                # Nasty workaround due to this not working on MacOSx
                if Platform.OS == 'MacOSX':
                    Log.Debug("Mac detected")
                    log = os.fdopen(os.open(zipFileName, os.O_RDONLY))
                    with log as f:
                        try:
                            while True:
                                fbuffer = f.read(4096)
                                if fbuffer:
                                    req.write(fbuffer)
                                else:
                                    f.close()
                                    req.finish()
                                    # remove temp zip file again
                                    os.remove(zipFileName)
                                    return req
                        except Exception, e:
                            Log.Exception(
                                'Fatal error happened in Logs \
                                download: ' + str(e))
                            req.clear()
                            req.set_status(500)
                            req.finish(
                                'Fatal error happened in Logs \
                                download: ' + str(e))
                    f.close()
                else:
                    with io.open(zipFileName, 'rb') as f:
                        try:
                            while True:
                                fbuffer = f.read(4096)
                                if fbuffer:
                                    req.write(fbuffer)
                                else:
                                    f.close()
                                    req.finish()
                                    # remove temp zip file again
                                    os.remove(zipFileName)
                                    return req
                        except Exception, e:
                            Log.Exception(
                                'Fatal error happened in Logs \
                                download: ' + str(e))
                            req.clear()
                            req.set_status(500)
                            req.finish(
                                'Fatal error happened in Logs \
                                download: ' + str(e))
            else:
                try:
                    if 'com.plexapp' in fileName:
                        file = os.path.join(
                            self.LOGDIR, 'PMS Plugin Logs', fileName)
                    else:
                        file = os.path.join(self.LOGDIR, fileName)
                    file = String.Unquote(file, usePlus=False)
                    retFile = []
                    if Platform.OS == 'MacOSX':
                        f = os.fdopen(os.open(file, os.O_RDONLY))
                        with f as content_file:
                            content = content_file.readlines()
                            for line in content:
                                retFile.append(line.strip())
                        f.close()
                        req.set_header(
                            'Content-Disposition',
                            'attachment; filename="' + fileName + '"')
                        req.set_header(
                            'Content-Type', 'application/text/plain')
                        req.set_header('Cache-Control', 'no-cache')
                        req.set_header('Pragma', 'no-cache')
                        for line in retFile:
                            req.write(line + '\n')
                        req.finish()
                        return req
                    else:
                        with io.open(
                                file, 'rb', errors='ignore') as content_file:
                            content = content_file.readlines()
                            for line in content:
                                retFile.append(line.strip())
                        req.set_header(
                            'Content-Disposition',
                            'attachment; filename="' + fileName + '"')
                        req.set_header(
                            'Content-Type', 'application/text/plain')
                        req.set_header('Cache-Control', 'no-cache')
                        req.set_header('Pragma', 'no-cache')
                        for line in retFile:
                            req.write(line + '\n')
                        req.finish()
                        return req
                except Exception, e:
                    Log.Exception(
                        'Fatal error happened in Logs download: ' + str(e))
                    req.clear()
                    req.set_status(500)
                    req.finish(
                        'Fatal error happened in Logs download: ' + str(e))
        except Exception, e:
            Log.Exception('Fatal error happened in Logs download: ' + str(e))
            req.clear()
            req.set_status(500)
            req.finish('Fatal error happened in Logs download: ' + str(e))

    @classmethod
    def SHOW(self, req, *args):
        '''
        This will return contents of the logfile as an array.
        Req. a parameter named fileName
        '''
        try:
            self.init()
            if args is None:
                fileName = ''
            else:
                if len(args) > 0:
                    fileName = list(args)[0][0]
                else:
                    fileName = ''
            if fileName == '':
                req.clear()
                req.set_status(412)
                req.finish('Missing fileName of log to show')
                return req
            fileName = String.Unquote(fileName, usePlus=False)
            if 'com.plexapp' in fileName:
                file = os.path.join(self.LOGDIR, 'PMS Plugin Logs', fileName)
            else:
                file = os.path.join(self.LOGDIR, fileName)
            retFile = []
            try:
                Log.Debug('Opening logfile: %s' % file)
                # with io.open(file, 'r', errors='ignore') as content_file:
                # Nasty workaround due to this not working on MacOSx
                if Platform.OS == 'MacOSX':
                    f = os.fdopen(os.open(file, os.O_RDONLY))
                    with f as content_file:
                        content = content_file.readlines()
                        for line in content:
                            retFile.append(line.strip())
                    f.close()
                else:
                    with io.open(file, 'r', errors='ignore') as content_file:
                        content = content_file.readlines()
                        for line in content:
                            retFile.append(line.strip())
                req.clear()
                req.set_status(200)
                req.set_header(
                    'Content-Type', 'application/json; charset=utf-8')
                req.finish(json.dumps(retFile))
            except Exception, e:
                Log.Exception('Fatal error happened in Logs show: ' + str(e))
                req.clear()
                req.set_status(404)
                req.finish('Fatal error happened in Logs show: ' + str(e))
        except Exception, e:
            Log.Exception('Fatal error happened in Logs show: ' + str(e))
            req.clear()
            req.set_status(500)
            req.finish('Fatal error happened in Logs show: ' + str(e))

    @classmethod
    def LIST(self, req, *args):
        '''
        This metode will return a list of logfiles. accepts a filter parameter
        '''
        Log.Debug('Starting Logs.List function')
        try:
            self.init()
            if args is None:
                fileFilter = ''
            else:
                if len(args) > 0:
                    fileFilter = list(args)[0][0]
                else:
                    fileFilter = ''
            retFiles = []
            Log.Debug('List logfiles called for directory %s' % (self.LOGDIR))
            for root, dirs, files in os.walk(self.LOGDIR, topdown=True):
                # Only list from the default directories
                dirs[:] = [d for d in dirs if d in ['PMS Plugin Logs']]
                path = root.split('/')
                for filename in files:
                    if Platform.OS == 'MacOSX':
                        if filename == ".DS_Store":
                            continue
                    if fileFilter != '':
                        if fileFilter.upper() in filename.upper():
                            ext = os.path.splitext(filename)[1].upper()[1:]
                            if ((ext == 'LOG') or (ext.isdigit())):
                                retFiles.append(filename)
                    else:
                        ext = os.path.splitext(filename)[1].upper()[1:]
                        if ((ext == 'LOG') or (ext.isdigit())):
                            retFiles.append(filename)
            if retFiles == []:
                Log.Debug('Nothing found')
                req.clear()
                req.set_status(404)
                req.finish('Nothing found')
            else:
                Log.Debug('Returning %s' % retFiles)
                req.clear()
                req.set_status(200)
                req.set_header(
                    'Content-Type', 'application/json; charset=utf-8')
                req.finish(json.dumps(sorted(retFiles)))
        except Exception, e:
            Log.Exception('Fatal error happened in Logs list: ' + str(e))
            req.clear()
            req.set_status(500)
            req.finish('Fatal error happened in Logs list: ' + str(e))

    @classmethod
    def LISTTIME(self, req, *args):
        '''
        This metode will return a list of logfiles. accepts a filter parameter
        '''
        Log.Debug('Starting Logs.List function')
        try:
            self.init()
            if args is None:
                fileFilter = ''
            else:
                if len(args) > 0:
                    fileFilter = list(args)[0][0]
                else:
                    fileFilter = ''
            retFiles = []
            Log.Debug('List logfiles called for directory %s' % (self.LOGDIR))
            for root, dirs, files in os.walk(self.LOGDIR, topdown=True):
                # Only list from the default directories
                dirs[:] = [d for d in dirs if d in ['PMS Plugin Logs']]
                path = root.split('/')
                for filename in files:
                    if Platform.OS == 'MacOSX':
                        if filename == ".DS_Store":
                            continue
                    if fileFilter != '':
                        if fileFilter.upper() in filename.upper():
                            ext = os.path.splitext(filename)[1].upper()[1:]
                            if ((ext == 'LOG') or (ext.isdigit())):
                                if filename.startswith('com'):
                                    file = os.path.join(
                                        self.LOGDIR,
                                        'PMS Plugin Logs',
                                        filename)
                                else:
                                    file = os.path.join(
                                        self.LOGDIR,
                                        filename)
                                entry = {}
                                entry[filename] = {
                                    'time': time.ctime(
                                        os.path.getmtime(file)),
                                    'unixstamp': os.path.getmtime(file)}
                                retFiles.append(entry)
                    else:
                        ext = os.path.splitext(filename)[1].upper()[1:]
                        if ((ext == 'LOG') or (ext.isdigit())):
                            if filename.startswith('com'):
                                file = os.path.join(
                                    self.LOGDIR,
                                    'PMS Plugin Logs',
                                    filename)
                            else:
                                file = os.path.join(
                                    self.LOGDIR,
                                    filename)
                            entry = {}
                            entry[filename] = {
                                'time': time.ctime(
                                    os.path.getmtime(file)),
                                'unixstamp': os.path.getmtime(file)}
                            retFiles.append(entry)
            if retFiles == []:
                Log.Debug('Nothing found')
                req.clear()
                req.set_status(404)
                req.finish('Nothing found')
            else:
                Log.Debug('Returning %s' % retFiles)
                req.clear()
                req.set_status(200)
                req.set_header(
                    'Content-Type', 'application/json; charset=utf-8')
                req.finish(json.dumps(sorted(retFiles)))
        except Exception, e:
            Log.Exception('Fatal error happened in Logs list: ' + str(e))
            req.clear()
            req.set_status(500)
            req.finish('Fatal error happened in Logs list: ' + str(e))
