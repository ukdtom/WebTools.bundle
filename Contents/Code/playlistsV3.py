#!/usr/bin/env python
# -*- coding: utf-8 -*-
#############################################################################
# Playlist module unit
#
# Author: dane22, a Plex Community member
#
# WebTools module for handling playlists
#
#############################################################################
import time
import io
import os
import json
import datetime
import re
from misc import misc
from plextvhelper import plexTV
from consts import VALIDEXT, EXCLUDEELEMENTS, EXCLUDEFIELDS
import pmsV3


# TODO: Remove when Plex framework allows token in the header.
# Also look at copy, delete and list method
import urllib2
from xml.etree import ElementTree
# TODO End

FUNCTIONS = {
    "get": [
        "LIST", "DOWNLOAD"],
    "post": [
        "COPY", "IMPORT"],
    "delete": ["DELETE"]}

MEDIASTEPS = 25  # Amount of medias we ask for at a time

EXCLUDE = EXCLUDEELEMENTS + '&excludeFields=summary,tagline'

ROOTNODES = {'audio': 'Track', 'video': 'Video', 'photo': 'Photo'}

MEDIATYPES = {'Track': 10}


class playlistsV3(object):
    @classmethod
    def init(self):
        """Defaults used by the rest of the class"""
        self.getListsURL = misc.GetLoopBack() + '/playlists/all'

    @classmethod
    def IMPORT(self, req, *args):
        """This metode will import a playlist"""
        # Just init of internal stuff
        sName = None
        sType = None
        sSrvId = None
        bSameSrv = False

        ''' Order the playlist '''
        def orderPlaylist(playlistId, orgPlaylist, sType):
            try:
                rootNode = ROOTNODES[sType]
                # Now get the import list as it is now
                url = ''.join((
                    misc.GetLoopBack(),
                    '/playlists/',
                    playlistId,
                    '/items',
                    '?',
                    EXCLUDE))
                playListXML = XML.ElementFromURL(url)
                newList = {}
                # Grap the original one, and sort by ListId
                for lib in orgPlaylist:
                    for item in orgPlaylist[lib]:
                        newList[item['ListId']] = item['title']
                # Need a counter here, since HTTP
                # url differs from first to last ones
                counter = 0
                for item in sorted(newList):
                    # get playListItemId of item
                    xPathStr = "//" + rootNode + \
                        "[@title='" + newList[item] + "']/@playlistItemID"
                    itemToMove = str(playListXML.xpath(unicode(xPathStr))[0])
                    if counter == 0:
                        url = ''.join((
                            misc.GetLoopBack(),
                            '/playlists/',
                            playlistId,
                            '/items/',
                            itemToMove,
                            '/move'))
                        counter += 1
                        after = itemToMove
                    else:
                        url = ''.join((
                            misc.GetLoopBack(),
                            '/playlists/',
                            playlistId,
                            '/items/',
                            itemToMove,
                            '/move?after=',
                            after))
                        after = itemToMove
                    # Now move the darn thing
                    HTTP.Request(url, cacheTime=0,
                                 immediate=True, method="PUT")
            except Exception, e:
                Log.Exception(
                    'Exception in PlayList orderList was %s' % (str(e)))

        ''' PlayList already exists ? Return true/false '''
        def alreadyPresent(title):
            # Get a list of PlayLists
            playlists = XML.ElementFromURL(self.getListsURL)
            # Grap the titles
            playlists = ','.join(
                        map(
                            str, (
                                playlist.get(
                                    'title') for playlist in playlists)))
            for titleInPlayList in playlists.split(','):
                if title == titleInPlayList:
                    return True
            return False

        ''' Import a playlist '''
        def doImport(jsonItems, playlistType, playlistTitle):
            playlistSmart = (jsonItems.get('smart') == 1)
            # Make url for creation of playlist
            targetFirstUrl = ''.join((
                misc.GetLoopBack(),
                '/playlists?type=',
                playlistType,
                '&title=',
                String.Quote(playlistTitle),
                '&smart=0&uri=library://'))
            counter = 0
            for lib in jsonItems:
                if counter < 1:
                    targetFirstUrl += lib + '/directory//library/metadata/'
                    medias = ','.join(
                        map(str, (item['id'] for item in jsonItems[lib])))
                    targetFirstUrl += String.Quote(medias)
                    # First url for the post created,
                    # so send it, and grab the response
                    try:
                        response = HTTP.Request(
                            targetFirstUrl,
                            cacheTime=0,
                            immediate=True,
                            method="POST")
                        ratingKey = XML.ElementFromString(
                            response).xpath('Playlist/@ratingKey')[0]
                    except Exception, e:
                        Log.Exception(
                            'Exception creating first part of \
                            playlist was: %s' % (str(e)))
                    counter += 1
                else:
                    # Remaining as put
                    medias = ','.join(
                        map(str, (item['id'] for item in jsonItems[lib])))
                    targetSecondUrl = ''.join((
                        misc.GetLoopBack(),
                        '/playlists/',
                        ratingKey,
                        '/items?uri=library://',
                        lib,
                        '/directory//library/metadata/',
                        String.Quote(medias)))
                    HTTP.Request(targetSecondUrl, cacheTime=0,
                                 immediate=True, method="PUT")
            return ratingKey

        ''' Phrase phrase3Party playlist '''
        def phrase3Party(lines):
            # Placeholder for items to import
            items = {}
            Log.Info('Import file was 3Party')
            # We need to find out, if this is a regular m3u file,
            # or an extended one
            if '#EXTM3U' in lines[0].upper():
                extended = True
                Log.Info('Playlist was an extended one')
            elif '#M3U' in lines[0].upper():
                extended = False
                Log.Info('Playlist was an non-extended one')
            else:
                Log.Error('Import file does not start with the \
                line: #EXTM3U or #M3U')
                req.clear()
                req.set_status(406)
                req.finish(
                    'Seems like we are trying to import a file that \
                    is not a playlist!')
                return
            if extended:
                try:
                    for line in lines[5:len(lines):3]:
                        media = json.loads(lines[lineNo][1:])
                        id = media['Id']
                        item = {}
                        item['ListId'] = media['ListId']
                        item['LibraryUUID'] = media['LibraryUUID']
                        lineNo += 1
                        media = lines[lineNo][8:].split(',', 1)
                        item['title'] = media[1].split(' - ', 1)[1]
                        lineNo += 1
                        item['fileName'] = lines[lineNo]
                        items[id] = item
                        lineNo += 1
                    return items
                except IndexError:
                    pass
                except Exception, e:
                    Log.Exception('Exception happened in \
                    phrase3Party was %s' % str(e))
                    pass
                finally:
                    return items
            else:
                try:
                    # Guess the media type
                    sType = guessMediaType(
                        lines[2].replace('\r', '').replace('\n', ''))
                    # Get possibel libraries to scan
                    libs = getLibsOfType(sType)
                    # Get a key,value list of potential medias
                    mediaList = getFilesFromLib(libs, sType)
                    return
                    # print 'Ged MediaList', mediaList
                    # Log.Debug(
                    # '************** PMS contains *****************')
                    # Log.Debug(mediaList)
                    basic = {}
                    counter = 1
                    for line in lines[2:len(lines):3]:
                        basic[str(counter)] = line.replace(
                            '\r', '').replace('\n', '')
                        counter += 1
                    items['basic'] = basic
                    # print 'Ged Basic', basic

                    final = {}

                    for item in basic:
                        # print 'Ged ********', item, basic[item]
                        if basic[item] in mediaList:
                            print 'Ged fundet'
                        else:
                            print 'Ged missed'

                except IndexError:
                    pass
                except Exception, e:
                    Log.Exception('Exception happened in \
                    phrase3Party was %s' % (str(e)))
                    pass
                finally:
                    # print 'Ged own', items
                    return
                    # return items

        ''' Phrase our own playlist '''
        def phraseOurs(lines):
            # Placeholder for items to import
            items = {}
            Log.Debug('Import file was ours')
            ourLine = lines[2][1:].replace('None', '"None"')
            jsonLine = JSON.ObjectFromString(ourLine)
            sName = jsonLine['title']
            Log.Debug('Playlist name internally is %s' % sName)
            sType = jsonLine['playlistType']
            Log.Debug('Playlist type is %s' % sType)
            sSrvId = jsonLine['ServerID']
            smart = jsonLine['smart']
            Log.Debug('Playlist smart is %s' % smart)
            Log.Debug('ServerId this playlist belongs to is %s' % sSrvId)
            thisServerID = XML.ElementFromURL(
                misc.GetLoopBack() + '/identity').get('machineIdentifier')
            Log.Debug('Current Server id is %s' % thisServerID)
            bSameSrv = (thisServerID == sSrvId)
            lineNo = 5
            try:
                for line in lines[5:len(lines):3]:
                    if not line:
                        break
                    myLine = str(line[1:])
                    myLine = myLine.replace("None", str(-1))
                    media = JSON.ObjectFromString(myLine)
                    id = media['Id']
                    item = {}
                    item['ListId'] = media['ListId']
                    item['LibraryUUID'] = media['LibraryUUID']
                    lineNo += 1
                    media = lines[lineNo][8:].split(',', 1)
                    item['title'] = media[1].split(' - ', 1)[1]
                    lineNo += 1
                    item['fileName'] = lines[lineNo]
                    items[id] = item
                    lineNo += 1
                return items
            except IndexError:
                pass
            except Exception, e:
                Log.Exception('Exception happened in \
                phraseOurs was %s' % str(e))
                pass
            finally:
                return [sType, smart, items]

        """ *************** Main stuff here *********************** """

        returnResult = {}
        success = []
        failed = []
        # Payload Upload file present?
        if 'localFile' not in req.request.files:
            req.clear()
            req.set_status(412)
            req.finish(
                'Missing upload file parameter named \
                localFile from the payload')
        else:
            localFile = req.request.files['localFile'][0]['body']
        try:
            playlistTitle = req.request.files[
                'localFile'][
                    0][
                        'filename'].rsplit('.')[0]
            # Make into seperate lines
            lines = localFile.split('\n')
            # Start by checking if we have a valid playlist file
            if 'M3U' not in lines[0].upper():
                Log.Error('Import file does not start with \
                the line: #EXTM3U or #M3U')
                req.clear()
                req.set_status(406)
                req.finish(
                    'Seems like we are trying to import a file \
                    that is not a playlist!')
                return
            if alreadyPresent(playlistTitle):
                Log.Error('Playlist %s already exists' % playlistTitle)
                req.clear()
                req.set_status(406)
                req.finish('Aborted, since playlist "%s" already \
                existed' % playlistTitle)
                return
            # Let's check if it's one of ours
            bOurs = (lines[1] == '#Written by WebTools for Plex')
            if bOurs:
                sType, smart, items = phraseOurs(lines)
            else:
                # REMOVE THIS WHEN DOING 3.PARTY IMPORT
                # Abort, since not ours
                Log.Error('Playlist is not ours')
                req.clear()
                req.set_status(415)
                req.finish('Aborted, since not our playlist')
                return
                '''
                # TODO: Code below for 3.Party import
                items = phrase3Party(lines)
                sType = guessMediaType(items)
            #return
                '''
            # Now validate the entries
            finalItems = {}
            for item in items:
                if checkItemIsValid(item, items[item]['title'], sType):
                    finalItem = {}
                    finalItem['id'] = item
                    finalItem['title'] = items[item]['title']
                    finalItem['ListId'] = items[item]['ListId']
                    if items[item]['LibraryUUID'] in finalItems:
                        finalItems[items[item]['LibraryUUID']].append(
                            finalItem)
                    else:
                        finalItems[items[item]['LibraryUUID']] = []
                        finalItems[items[item]['LibraryUUID']].append(
                            finalItem)
                    success.append(items[item]['title'])
                else:
                    Log.Debug('Could not find item with a title of %s' %
                              items[item]['title'])
                    result = searchForItemKey(items[item]['title'], sType)
                    if result is not None:
                        finalItem = {}
                        finalItem['id'] = result[0]
                        finalItem['title'] = items[item]['title']
                        finalItem['ListId'] = items[item]['ListId']
                        if result[1] in finalItems:
                            finalItems[result[1]].append(finalItem)
                        else:
                            finalItems[result[1]] = []
                            finalItems[result[1]].append(finalItem)
                        success.append(unicode(items[item]['title']))
                    else:
                        failed.append(items[item]['title'])
                        Log.Error('Item %s was not found' %
                                  items[item]['title'])
            ratingKey = doImport(finalItems, sType, playlistTitle)
            if not smart:
                # Now order the playlist
                orderPlaylist(ratingKey, finalItems, sType)
            returnResult['success'] = success
            returnResult['failed'] = failed
            Log.Info('Import returned %s' %
                     (json.dumps(returnResult, ensure_ascii=False)))
            req.clear()
            req.set_status(200)
            req.finish(json.dumps(returnResult, ensure_ascii=False))
        except Exception, e:
            Log.Exception(
                'Exception happened in Playlist import was: %s' % (str(e)))
            req.clear()
            req.set_status(500)
            req.finish(
                'Exception happened in Playlist import was: %s' % (str(e)))
        return

    @classmethod
    def COPY(self, req, *args):
        """
        This metode will copy a playlist. between users
        Params:
        key : Key of PlayList to copy
        UserTo : ID of target User to copy Playlist to
            * If UserTo is -1 or None, then target user is owner
            * If UserTo is -2, then target user is all users
        UserFrom : Id of Source user having the PlayList
            * If UserFrom is -1 or None, then UserFrom is owner
        """
        users = None
        # Get user list, among with access token
        users = plexTV().getUserList()
        # Start by getting the key of the PlayList
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
            # Get UserFrom
            if 'userfrom' in arguments:
                # Get the userfrom
                userfrom = arguments[arguments.index('userfrom') + 1]
                if userfrom == '-1':
                    userfrom = None
                elif userfrom == '-2':
                    Log.Critical('All selected as from')
                    req.clear()
                    req.set_status(405)
                    req.finish("We can't have all users as the source")
                elif userfrom not in users:
                    req.clear()
                    req.set_status(404)
                    req.finish("UserFrom not found")
            else:
                # Copy from the Owner
                userfrom = None
            # Get UserTo
            if 'userto' in arguments:
                # Get the userto
                userto = arguments[arguments.index('userto') + 1]
                if userto == '-1':
                    userto = None
            else:
                userto = None
            # Get the playlist that needs to be copied
            url = ''.join((
                misc.GetLoopBack(),
                '/playlists/',
                key,
                '/items?',
                EXCLUDE))
            # Get User Token
            if userfrom:
                userToken = users[userfrom]['accessToken']
            else:
                userToken = None
            # Get the playlist
            jsonItems = getPlayListAsJSON(userToken, key, copyAsSmart=True)
            playlistTitle = jsonItems['playlistTitle']
            playlistType = jsonItems['playlistType']
            # Now split items into smaller chunks, defined by MEDIASTEPS
            itemsToAdd = {}
            for libDir in jsonItems['items']:
                itemsToAdd[libDir] = misc.chunks(
                                            jsonItems[
                                                'items'][
                                                    libDir], MEDIASTEPS)
            try:
                # So we got all the info needed now from the source user,
                # now time for the target user
                urltoPlayLists = misc.GetLoopBack() + '/playlists?' + EXCLUDE
                if userto is None:
                    # Target is the owner
                    Log.Debug('Target user is the owner')
                    print 'Ged target is owner'
                    playlistto = XML.ElementFromURL(urltoPlayLists)
                    # So we got the target users list of playlists, and if
                    # the one we need to copy already is there, we delete it
                    for itemto in playlistto:
                        if playlistTitle == itemto.get('title'):
                            keyto = itemto.get('ratingKey')
                            deletePlayListforUsr(req, keyto, None)

                    # Make url for creation of playlist
                    targetFirstUrl = ''.join((
                        misc.GetLoopBack(),
                        '/playlists?type=',
                        playlistType,
                        '&title=',
                        String.Quote(playlistTitle),
                        '&smart=0&uri=library://'))
                    bFirstRun = True
                    # for lib in jsonItems['items']:
                    for lib in itemsToAdd:
                        for items in lib:
                            if bFirstRun:
                                targetFirstUrl += ''.join((
                                    lib,
                                    '/directory//library/metadata/'))
                                medias = ','.join(map(
                                    str, jsonItems['items'][lib]))
                                targetFirstUrl += String.Quote(medias)
                                # First url for the post created, so send it,
                                # and grab the response
                                try:
                                    response = HTTP.Request(
                                        targetFirstUrl,
                                        cacheTime=0,
                                        immediate=True,
                                        method="POST")
                                    ratingKey = XML.ElementFromString(
                                        response).xpath(
                                            'Playlist/@ratingKey')[0]
                                except Exception, e:
                                    Log.Exception(
                                        'Exception creating first part \
                                        of playlist was: %s' % (str(e)))
                                bFirstRun = False
                            else:
                                # Remaining as put
                                medias = ','.join(map(str, jsonItems[lib]))
                                targetSecondUrl = ''.join((
                                    misc.GetLoopBack(),
                                    '/playlists/',
                                    ratingKey,
                                    '/items?uri=library://',
                                    lib,
                                    '/directory//library/metadata/',
                                    String.Quote(medias)))
                                HTTP.Request(
                                    targetSecondUrl,
                                    cacheTime=0,
                                    immediate=True,
                                    method="PUT")
                elif userto.upper() == '-2':
                    Log.Info('Copy to all users')
                    print 'Ged 1', users
                    for user in users:
                        print 'Ged2 user', user
                        try:
                            # TODO Change to native framework call, when
                            # Plex allows token in header
                            opener = urllib2.build_opener(urllib2.HTTPHandler)
                            request = urllib2.Request(urltoPlayLists)
                            request.add_header(
                                'X-Plex-Token', users[user]['accessToken'])
                            response = opener.open(request).read()
                            playlistto = XML.ElementFromString(response)
                        except Ex.HTTPError, e:
                            Log.Exception(
                                'HTTP exception when downloading a \
                                playlist for the user was: %s' % (e))
                            req.clear()
                            req.set_status(e.code)
                            req.finish(str(e))
                        except Exception, e:
                            Log.Exception(
                                'Exception happened when downloading a \
                                playlist for the user was: %s' % (str(e)))
                            req.clear()
                            req.set_status(500)
                            req.finish(
                                'Exception happened when downloading a \
                                playlist for the user was: %s' % (str(e)))
                        # So we got the target users list of playlists, and
                        # if the one we need to copy already is there,
                        # we delete it
                        for itemto in playlistto:
                            if playlistTitle == itemto.get('title'):
                                keyto = itemto.get('ratingKey')
                                deletePlayListforUsr(
                                    req, keyto, users[user]['accessToken'])
                        # Make url for creation of playlist
                        targetFirstUrl = ''.join((
                            misc.GetLoopBack(),
                            '/playlists?type=',
                            playlistType,
                            '&title=',
                            String.Quote(playlistTitle),
                            '&smart=0&uri=library://'))
                        counter = 0
                        for lib in jsonItems:
                            if counter < 1:
                                targetFirstUrl += ''.join((
                                    lib,
                                    '/directory//library/metadata/'))
                                medias = ','.join(map(str, jsonItems[lib]))
                                targetFirstUrl += String.Quote(medias)
                                # First url for the post created, so send it,
                                # and grab the response
                                try:
                                    opener = urllib2.build_opener(
                                        urllib2.HTTPHandler)
                                    request = urllib2.Request(
                                        targetFirstUrl)
                                    request.add_header(
                                        'X-Plex-Token',
                                        users[user]['accessToken'])
                                    request.get_method = lambda: 'POST'
                                    response = opener.open(request).read()
                                    ratingKey = XML.ElementFromString(
                                        response).xpath(
                                            'Playlist/@ratingKey')[0]
                                except Exception, e:
                                    Log.Exception(
                                        'Exception creating first part of \
                                        playlist was: %s' % (str(e)))
                                counter += 1
                            else:
                                # Remaining as put
                                medias = ','.join(map(str, jsonItems[lib]))
                                targetSecondUrl = ''.join((
                                    misc.GetLoopBack(),
                                    '/playlists/',
                                    ratingKey,
                                    '/items?uri=library://',
                                    lib,
                                    '/directory//library/metadata/',
                                    String.Quote(medias)))
                                opener = urllib2.build_opener(
                                    urllib2.HTTPHandler)
                                request = urllib2.Request(targetSecondUrl)
                                request.add_header(
                                    'X-Plex-Token', users[user]['accessToken'])
                                request.get_method = lambda: 'PUT'
                                opener.open(request)
                else:
                    try:
                        # TODO Change to native framework call, when Plex
                        # allows token in header
                        opener = urllib2.build_opener(urllib2.HTTPHandler)
                        request = urllib2.Request(urltoPlayLists)
                        request.add_header(
                            'X-Plex-Token', users[userto]['accessToken'])
                        response = opener.open(request).read()
                        playlistto = XML.ElementFromString(response)
                    except Ex.HTTPError, e:
                        Log.Exception(
                            'HTTP exception when downloading a playlist \
                            for the owner was: %s' % (e))
                        req.clear()
                        req.set_status(e.code)
                        req.finish(str(e))
                    except Exception, e:
                        Log.Exception(
                            'Exception happened when downloading a \
                            playlist for the user was: %s' % (str(e)))
                        req.clear()
                        req.set_status(500)
                        req.finish(
                            'Exception happened when downloading a \
                            playlist for the user was: %s' % (str(e)))
                    # So we got the target users list of playlists, and if
                    # the one we need to copy already is there, we delete it
                    for itemto in playlistto:
                        if playlistTitle == itemto.get('title'):
                            keyto = itemto.get('ratingKey')
                            deletePlayListforUsr(
                                req, keyto, users[userto]['accessToken'])
                    # Make url for creation of playlist
                    targetFirstUrl = ''.join((
                        misc.GetLoopBack(),
                        '/playlists?type=',
                        playlistType,
                        '&title=',
                        String.Quote(playlistTitle),
                        '&smart=0&uri=library://'))
                    # counter = 0
                    bFirstRun = True
                    for lib in jsonItems['items']:
                        if bFirstRun:
                            targetFirstUrl += ''.join((
                                lib,
                                '/directory/library/metadata/'))
                            medias = ','.join((
                                        map(
                                            str, jsonItems[
                                                'items'][lib])))
                            targetFirstUrl += String.Quote(medias)
                            # First url for the post created, so send it,
                            # and grab the response
                            try:
                                opener = urllib2.build_opener(
                                    urllib2.HTTPHandler)
                                request = urllib2.Request(targetFirstUrl)
                                request.add_header(
                                    'X-Plex-Token',
                                    users[userto]['accessToken'])
                                request.get_method = lambda: 'POST'
                                response = opener.open(request).read()
                                ratingKey = XML.ElementFromString(
                                    response).xpath('Playlist/@ratingKey')[0]
                            except Exception, e:
                                Log.Exception(
                                    'Exception creating first part \
                                    of playlist was: %s' % (str(e)))
                            # counter += 1
                            bFirstRun = False
                        else:
                            # Remaining as put
                            medias = ','.join((
                                        map(
                                            str, jsonItems[
                                                'items'][lib])))
                            targetSecondUrl = ''.join((
                                misc.GetLoopBack(),
                                '/playlists/',
                                ratingKey,
                                '/items?uri=library://',
                                lib,
                                '/directory//library/metadata/',
                                String.Quote(medias)))
                            opener = urllib2.build_opener(urllib2.HTTPHandler)
                            request = urllib2.Request(targetSecondUrl)
                            request.add_header(
                                'X-Plex-Token', users[userto]['accessToken'])
                            request.get_method = lambda: 'PUT'
                            opener.open(request)

            except Exception, e:
                Log.Exception('Exception in CopyPlaylist was %s' % str(e))
        else:
            Log.Critical('Missing Arguments')
            req.clear()
            req.set_status(412)
            req.finish('Missing Arguments')

    @classmethod
    def DOWNLOAD(self, req, *args):
        """This metode will download a playlist. accepts a user parameter"""
        try:
            user = None
            if args is not None:
                # We got additional arguments
                if len(args) > 0:
                    # Get them in lower case
                    arguments = [item.lower() for item in list(args)[0]]
                    if 'user' in arguments:
                        # Get key of the user
                        user = arguments[arguments.index('user') + 1]
                # So now user is either none (Owner) or a keyId of a user
                # Now lets get the key of the playlist
                if 'key' in arguments:
                    # Get key of the user
                    key = arguments[arguments.index('key') + 1]
                    url = ''.join((
                        misc.GetLoopBack(),
                        '/playlists/',
                        key,
                        '/items',
                        '?',
                        EXCLUDE))
                else:
                    Log.Error('Missing key of playlist')
                    req.clear()
                    req.set_status(412)
                    req.finish('Missing key of playlist')
                try:
                    Log.Info('downloading playlist with ID: %s' % key)
                    try:
                        title, playList = getPlayListItems(user, key)
                        # Replace invalid caracters for a
                        # filename with underscore
                        fileName = re.sub('[\/[:#*?"<>|]', '_', title).strip()
                        fileName += '.m3u8'
                        req.set_header(
                            'Content-Disposition',
                            'attachment; filename="' + fileName + '"')
                        req.set_header('Cache-Control', 'no-cache')
                        req.set_header('Pragma', 'no-cache')
                        req.set_header(
                            'Content-Type',
                            'application/text/plain')
                        # start writing
                        for line in playList:
                            # print line
                            req.write(unicode(line))
                        req.set_status(200)
                        req.finish()
                    except Exception, e:
                        Log.Exception('Exception when downloading a playlist \
                        as the owner was %s' % str(e))
                        Log.Debug('Trying to get more info here')
                        req.clear()
                        req.set_status(500)
                        req.finish(str(e))
                except Ex.HTTPError, e:
                    Log.Exception(
                        'HTTP exception  when downloading a playlist for \
                        the owner was: %s' % (e))
                    req.clear()
                    req.set_status(500)
                    req.finish(str(e))
                except Exception, e:
                    Log.Exception(
                        'Exception happened when downloading a playlist \
                        for the owner was: %s' % (str(e)))
                    req.clear()
                    req.set_status(500)
                    req.finish(
                        'Exception happened when downloading a playlist \
                        for the owner was: %s' % (str(e)))
        except Exception, e:
            Log.Exception(
                'Fatal error happened in playlists.download: ' + str(e))
            req.clear()
            req.set_status(500)
            req.finish(
                'Fatal error happened in playlists.download: %s' % (str(e)))

    @classmethod
    def DELETE(self, req, *args):
        """This metode will delete a playlist. accepts a user parameter"""
        try:
            user = None
            if args is not None:
                # We got additional arguments
                if len(args) > 0:
                    # Get them in lower case
                    arguments = [item.lower() for item in list(args)[0]]
                    if 'user' in arguments:
                        # Get key of the user
                        user = arguments[arguments.index('user') + 1]
                # So now user is either none (Owner) or a keyId of a user
                # Now lets get the key of the playlist
                if 'key' in arguments:
                    # Get key of the user
                    key = arguments[arguments.index('key') + 1]
                    url = misc.GetLoopBack() + '/playlists/' + key
                else:
                    Log.Error('Missing key of playlist')
                    req.clear()
                    req.set_status(412)
                    req.finish('Missing key of playlist')
            if user is None:
                try:
                    # Delete playlist from the owner
                    Log.Info('Deleting playlist with ID: %s' % key)
                    HTTP.Request(url, cacheTime=0,
                                 immediate=True, method="DELETE")
                except Ex.HTTPError, e:
                    Log.Exception(
                        'HTTP exception  when deleting a playlist \
                        for the owner was: %s' % (e))
                    req.clear()
                    req.set_status(e.code)
                    req.finish(str(e))
                except Exception, e:
                    Log.Exception(
                        'Exception happened when deleting a playlist \
                        for the owner was: %s' % (str(e)))
                    req.clear()
                    req.set_status(500)
                    req.finish(
                        'Exception happened when deleting a playlist \
                        for the owner was: %s' % (str(e)))
            else:
                # We need to logon as a user in order to nuke the playlist
                try:
                    # Get user list, among with their access tokens
                    users = plexTV().getUserList()
                    # Detele the playlist
                    deletePlayListforUsr(req, key, users[user]['accessToken'])
                except Ex.HTTPError, e:
                    Log.Exception(
                        'HTTP exception when deleting a \
                        playlist for the owner was: %s' % (e))
                    req.clear()
                    req.set_status(e.code)
                    req.finish(str(e))
                except Exception, e:
                    Log.Exception(
                        'Exception happened when deleting a \
                        playlist for the user was: %s' % (str(e)))
                    req.clear()
                    req.set_status(500)
                    req.finish(
                        'Exception happened when deleting a playlist \
                        for the user was: %s' % (str(e)))
        except Exception, e:
            Log.Exception(
                'Fatal error happened in playlists.delete: ' + str(e))
            req.clear()
            req.set_status(500)
            req.finish(
                'Fatal error happened in playlists.delete: %s' % (str(e)))

    @classmethod
    def LIST(self, req, *args):
        """
        This metode will return a list of playlists.
        accepts a user parameter
        """
        try:
            user = None
            if args is not None:
                # We got additional arguments
                if len(args) > 0:
                    # Get them in lower case
                    arguments = [item.lower() for item in list(args)[0]]
                    if 'user' in arguments:
                        # Get key of the user
                        user = arguments[arguments.index('user') + 1]
            # So now user is either none or a keyId
            if user is None:
                playlists = XML.ElementFromURL(self.getListsURL)
            else:
                # Darn....Hard work ahead..We have to
                # logon as another user here :-(
                users = plexTV().getUserList()
                myHeader = {}
                myHeader['X-Plex-Token'] = users[user]['accessToken']
                # TODO Change to native framework call, when Plex
                # allows token in header
                request = urllib2.Request(self.getListsURL, headers=myHeader)
                playlists = XML.ElementFromString(
                    urllib2.urlopen(request).read())
            result = {}
            for playlist in playlists:
                id = playlist.get('ratingKey')
                result[id] = {}
                result[id]['title'] = playlist.get('title')
                result[id]['summary'] = playlist.get('summary')
                result[id]['smart'] = playlist.get('smart')
                result[id]['playlistType'] = playlist.get('playlistType')
            req.set_status(200)
            req.set_header('Content-Type', 'application/json; charset=utf-8')
            req.finish(json.dumps(result))
        except Exception, e:
            Log.Exception('Fatal error happened in playlists.list: ' + str(e))
            req.clear()
            req.set_status(500)
            req.finish('Fatal error happened in playlists.list: %s' % (str(e)))

    @classmethod
    def getFunction(self, metode, req):
        """Get the relevant function and call it with params"""
        self.init()
        function, params = misc.getFunction(FUNCTIONS, metode, req)
        if function is None:
            Log.Debug('Function to call is None')
            req.clear()
            req.set_status(404)
            req.finish('Unknown function call')
        else:
            try:
                if params is None:
                    getattr(self, function)(req)
                else:
                    getattr(self, function)(req, params)
            except Exception, e:
                Log.Exception('Exception in process of: ' + str(e))


# ************************ Internal functions ************************

def deletePlayListforUsr(req, key, token):
    url = misc.GetLoopBack() + '/playlists/' + key
    if token is None:
        HTTP.Request(url, cacheTime=0, immediate=True, method="DELETE")
    else:
        try:
            # TODO Change to native framework call, when
            # Plex allows token in header
            opener = urllib2.build_opener(urllib2.HTTPHandler)
            request = urllib2.Request(url)
            request.add_header('X-Plex-Token', token)
            request.get_method = lambda: 'DELETE'
            url = opener.open(request)
        except Ex.HTTPError, e:
            Log.Exception(
                'HTTP exception  when deleting a playlist for \
                the owner was: %s' % (e))
            req.clear()
            req.set_status(e.code)
            req.finish(str(e))
        except Exception, e:
            Log.Exception(
                'Exception happened when deleting a playlist for \
                the user was: %s' % (str(e)))
            req.clear()
            req.set_status(500)
            req.finish(
                'Exception happened when deleting a playlist for \
                the user was: %s' % (str(e)))
    return req


def checkItemIsValid(key, title, sType):
    """This function returns true or false, if key/path matches for a media"""
    url = misc.GetLoopBack() + '/library/metadata/' + str(key) + '?' + EXCLUDE
    mediaTitle = None
    try:
        mediaTitle = XML.ElementFromURL(url).xpath(
            '//' + ROOTNODES[sType])[0].get('title')
    except:
        pass
    return (title == mediaTitle)


def searchForItemKey(title, sType):
    """This function will search for a a media based on
    title and type, and return the key"""
    try:
        result = []
        # TODO: Fix for other types
        # Are we talking about a video here?
        url = misc.GetLoopBack() + '/search?type=10&query=' + \
            String.Quote(title) + '&' + EXCLUDE
        found = XML.ElementFromURL(url)
        ratingKey = found.xpath('//' + ROOTNODES[sType] + '/@ratingKey')[0]
        result.append(ratingKey)
        librarySectionUUID = found.xpath(
            '//' + ROOTNODES[sType] + '/@librarySectionUUID')[0]
        result.append(librarySectionUUID)
        Log.Info('Item named %s was located as item with key %s' %
                 (title, ratingKey))
        return result
    except Exception, e:
        pass


def guessMediaType(fileName):
    """Here we detect the Plex type of a media file"""
    sType = None
    # Get ext of the file
    ext = os.path.splitext(fileName)[1][1:]
    for mediaType in VALIDEXT:
        if ext in VALIDEXT[mediaType]:
            sType = mediaType
    return sType


def getLibsOfType(sType):
    """Get libraries of a certain type"""
    libsToSearch = []
    if sType == 'audio':
        sType = 'artist'
    # Getting a list of all libraries
    try:
        url = misc.GetLoopBack() + '/library/sections/all'
        xPathStr = 'Directory[@type="' + sType + '"]'
        libs = XML.ElementFromURL(url).xpath(xPathStr)
        for lib in libs:
            libsToSearch.append(lib.get('key'))
        Log.Info('Need to serch the following \
        libraries: %s' % str(libsToSearch))
        return libsToSearch
    except Exception, e:
        Log.Exception('Exception in playList getLibsOfType was %s' % str(e))
    return


def getFilesFromLib(libs, sType):
    """Get media files from filePath"""
    itemList = {}
    # Add from one library at a time
    for lib in libs:
        start = 0  # Start point of items
        baseUrl = ''.join((
            misc.GetLoopBack(),
            '/library/sections/',
            lib,
            '/all?type=',
            str(MEDIATYPES[ROOTNODES[sType]]),
            '&',
            EXCLUDE,
            '&X-Plex-Container-Start='))
        url = baseUrl + '0' + '&X-Plex-Container-Size=0'
        libInfo = XML.ElementFromURL(url)
        # Now get the amount of items we need to add
        totalSize = libInfo.get('totalSize')
        # Now get the UUID of the library
        librarySectionUUID = libInfo.get('librarySectionUUID')
        try:
            while int(start) < int(totalSize):
                url = ''.join((
                    baseUrl,
                    str(start),
                    '&X-Plex-Container-Size=',
                    str(MEDIASTEPS)))
                medias = XML.ElementFromURL(url)
                for media in medias:
                    parts = media.xpath('//Media/Part')
                    for part in parts:
                        mediaInfo = {}
                        item = {}
                        mediaInfo = {
                            'fullFileName': part.get('file'),
                            'librarySectionUUID': librarySectionUUID}
                        key = media.get('ratingKey')
                        item[key] = [mediaInfo]
                        itemList[os.path.basename(part.get('file'))] = item
                start += MEDIASTEPS
        except Exception, e:
            Log.Exception('exception in getFilesFromLib was: %s' % str(e))

    Log.Debug('******** getFilesFromLib **********')
    Log.Debug(itemList)
    return itemList


def getPlayListItems(user, key):
    """
    Params:
    user : key of user, or null if the owner
    key : key of playlist
    Return [title, playlist]
    """
    Log.Info('Starting getPlaylistItems with \
    user: %s and key of: %s' % (user, key))
    playlist = []
    infoURL = misc.GetLoopBack() + '/playlists/' + key
    userToken = None
    if user:
        # Shared or Home user
        try:
            # Get user list, among with their access tokens
            users = plexTV().getUserList()
            userToken = users[user]['accessToken']
            # TODO Change to native framework call,
            # when Plex allows token in header
        except Exception, e:
            Log.Exception('Exception getting the token \
            for a user was: %s' % str(e))
            return None
    try:
        info = getXMLElement(userToken, infoURL).xpath('//Playlist')[0]
    except Exception, e:
        Log.Exception('Exception getting info was: %s' % str(e))
        return None
    try:
        title = info.get('title')
        # Start adding to the array
        playlist.append(unicode("#EXTM3U\n"))
        playlist.append(unicode("#Written by WebTools for Plex\n"))
        jsonLine = {}
        jsonLine["title"] = title
        jsonLine["smart"] = info.get('smart')
        jsonLine["leafCount"] = info.get('leafCount')
        content = info.get('content')
        if content:
            content = content[
                content.index('library', content.index('library')+1):]
        jsonLine["content"] = content
        playListType = info.get('playlistType')
        jsonLine["playlistType"] = playListType
        jsonLine["ServerID"] = XML.ElementFromURL(
            misc.GetLoopBack() + '/identity').get('machineIdentifier')
        Log.Debug('getPlayListItems returning: %s' % str(jsonLine))
        # Switch to double quotes, to make framework happy
        jsonLine = json.dumps(jsonLine)
        playlist.append(unicode("#" + str(jsonLine) + "\n"))
        playlist.append("#\n#\n")
    except Exception, e:
        Log.Exception('Exception in Download was %s' % str(e))
        return None
    start = 0
    while True:
        url = ''.join((
            misc.GetLoopBack(),
            '/playlists/',
            key,
            '/items?X-Plex-Container-Start=',
            str(start),
            '&X-Plex-Container-Size=',
            str(MEDIASTEPS)))
        response = getXMLElement(userToken, url)
        start += MEDIASTEPS
        if response.get('size') == '0':
            break
        try:
            root = '//' + ROOTNODES[playListType]
            for item in response.xpath(root):
                # Get the Library UUID
                itemURL = ''.join((
                    misc.GetLoopBack(),
                    '/library/metadata/',
                    item.get('ratingKey'),
                    '?',
                    EXCLUDE))
                libraryUUID = getXMLElement(
                    userToken, itemURL).get('librarySectionUUID')
                strLine = ''.join((
                    '#{"Id":',
                    item.get('ratingKey'),
                    ', "ListId":',
                    str(item.get('playlistItemID')),
                    ', "LibraryUUID":"',
                    libraryUUID,
                    '"}\n'))
                playlist.append(unicode(strLine))
                row = '#EXTINF:'
                # Get duration
                try:
                    duration = int(item.get('duration')) / 1000
                except:
                    duration = -1
                    pass
                row = row + str(duration) + ','
                # Audio List
                if playListType == 'audio':
                    try:
                        if item.get('originalTitle') is None:
                            row = row + item.get('grandparentTitle').replace(
                                ' - ', ' ') + ' - ' + item.get(
                                    'title').replace(' - ', ' ')
                        else:
                            row = row + item.get('originalTitle').replace(
                                ' - ', ' ') + ' - ' + item.get(
                                    'title').replace(' - ', ' ')
                    except Exception, e:
                        Log.Exception(
                            'Exception digesting an audio entry \
                            was %s' % (str(e)))
                        pass
                # Video
                elif playListType == 'video':
                    try:
                        entryType = item.get('type')
                        if entryType == 'movie':
                            # Movie
                            row = row + 'movie' + \
                                ' - ' + item.get('title')
                        else:
                            # Show
                            row = row + 'show' + \
                                ' - ' + item.get('title')
                    except Exception, e:
                        Log.Exception(
                            'Exception happened when digesting the line \
                            for Playlist was %s' % (str(e)))
                        pass
                # Pictures
                else:
                    row = row + 'Picture - ' + \
                        item.get('title').replace(' - ', ' ')
                playlist.append(unicode(row + '\n'))
                # Add file path
                playlist.append(
                    unicode(
                        item.xpath('Media/Part/@file')[0]) + '\n')
        except Exception, e:
            Log.Exception('Exception in getPlayListItems was: %s' % str(e))
            Log.Critical('Url to offending item was %s' % itemURL)
            return None
    return [title, playlist]


def getXMLElement(userToken, url):
    """
    Send the request to the server, and returns the respond as an XML element
    If an error happened, then return None
    Params:
    UserToken: None if Owner, else token
    url: Url to fetch info from
    """
    if not userToken:
        # User is the owner
        try:
            tmp = XML.ElementFromURL(url)
            return XML.ElementFromURL(url)
        except Exception, e:
            Log.Exception('Exception when getting a response \
            for %s as the owner was %s' % (url, str(e)))
            return None
    else:
        try:
            # TODO Change to native framework call, when
            # Plex allows token in header
            opener = urllib2.build_opener(urllib2.HTTPHandler)
            request = urllib2.Request(url)
            request.add_header(
                'X-Plex-Token', userToken)
            response = opener.open(request).read()
            return XML.ElementFromString(response)
        except Exception, e:
            Log.Exception('Exception when getting a \
            response for %s as a user was %s' % (url, str(e)))
            return None


def getPlayListAsJSON(userToken, key, copyAsSmart=False):
    """
    Gets a playlist from the PMS, and returns the respond as an XML element
    If an error happened, then return None
    Params:
    UserToken: None if Owner, else token
    key: key of playlist
    """
    print 'Ged789 getPlayListAsJSON triggered'
    # Start by getting initial info
    url = url = misc.GetLoopBack() + '/playlists/' + key
    initialInfo = getXMLElement(userToken, url).xpath('//Playlist')[0]
    playlistType = initialInfo.get('playlistType')
    playlistTitle = initialInfo.get('title')
    playlistSmart = (initialInfo.get('smart') == 1)
    content = initialInfo.get('content')
    playlist = {}
    # Add type, title and if smart
    playlist['playlistType'] = playlistType
    playlist['playlistTitle'] = playlistTitle
    playlist['playlistSmart'] = playlistSmart
    playlist['content'] = content
    print 'Ged test', playlistSmart, copyAsSmart
    if (playlistSmart and not copyAsSmart):
        print 'Ged 55444 return as SmartList only'
        # Now return the result
        Log.Debug('getPlayListAsJSON returning a playlist as:')
        Log.Debug(json.dumps(playlist))
        return playlist
    else:
        # Prepare the url
        url = misc.GetLoopBack() + '/playlists/' + key + '/items?' + EXCLUDE
        # Temp Storage
        jsonItemsTmp = {}
        # Where to start fetching from
        start = 0
        while True:
            url += ''.join((
                '&X-Plex-Container-Start=',
                str(start),
                '&X-Plex-Container-Size=',
                str(MEDIASTEPS)))
            print 'Ged1', url

            grab = getXMLElement(userToken, url)

            print 'Ged2 size', grab.get('size')

            ROOTNODE = ROOTNODES[playlistType]
            if grab.get('size') == '0':
                # Reached the end
                break
            else:
                start += MEDIASTEPS
            for item in grab.xpath('//' + ROOTNODE):
                ratingKey = int(item.get('ratingKey'))
                librarySectionID = int(item.get('librarySectionID'))
                if librarySectionID in jsonItemsTmp:
                    jsonItemsTmp[librarySectionID].append(ratingKey)
                else:
                    jsonItemsTmp[librarySectionID] = [ratingKey]
        # Now change librarySectionID into UUID
        jsonItems = {}
        for item in jsonItemsTmp:
            jsonItems[
                pmsV3.pmsV3().GETSECTIONKEYUUID(item)] = jsonItemsTmp[item]
        playlist['items'] = jsonItems
        # Now return the result
        Log.Debug('getPlayListAsJSON returning a playlist as:')
        Log.Debug(json.dumps(playlist))
        return playlist


def sendHTTPURL(url, token, method):
    """
    This will send an url to PMS, and
    return the response
    PARAMS:
    url : url to send
    token : token of user, or None for owner
    method: method of the request, like GET, PUT or POST
    """
    if user is None:
        print 'Ged send to owner'
        response = HTTP.Request(
                            url,
                            cacheTime=0,
                            immediate=True,
                            method=method)
    else:
        opener = urllib2.build_opener(
            urllib2.HTTPHandler)
        request = urllib2.Request(url)
        request.add_header(
            'X-Plex-Token', token)
        request.get_method = lambda: method
        response = opener.open(request)
    return response
