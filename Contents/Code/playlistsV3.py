######################################################################################################################
#	Playlist module unit
#
#	Author: dane22, a Plex Community member
#
# 	A WebTools module for handling playlists
#
######################################################################################################################
import time
import io
import os
import json
import datetime
import re
from misc import misc
from plextvhelper import plexTV
from uuid import uuid4
from consts import MEDIATYPE, VALIDEXT, EXCLUDEELEMENTS, EXCLUDEFIELDS


# TODO: Remove when Plex framework allows token in the header. Also look at delete and list method
import urllib2
from xml.etree import ElementTree
# TODO End


GET = ['LIST', 'DOWNLOAD']
PUT = []
POST = ['COPY', 'IMPORT']
DELETE = ['DELETE']

MEDIASTEPS = 25 # Amount of medias we ask for at a time

EXCLUDE = EXCLUDEELEMENTS + '&excludeFields=summary,tagline'

ROOTNODES = {'audio': 'Track', 'video': 'Video', 'photo': 'Photo'}

MEDIATYPES = {'Track' : 10}


class playlistsV3(object):
    ''' Defaults used by the rest of the class '''
    @classmethod
    def init(self):
        self.getListsURL = misc.GetLoopBack() + '/playlists/all'

    ''' This metode will import a playlist. '''
    @classmethod
    def IMPORT(self, req, *args):
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
                url = misc.GetLoopBack() + '/playlists/' + playlistId + '/items' + '?' + EXCLUDE
                playListXML = XML.ElementFromURL(url)
                newList = {}
                # Grap the original one, and sort by ListId
                for lib in orgPlaylist:
                    for item in orgPlaylist[lib]:
                        newList[item['ListId']] = item['title']
                # Need a counter here, since HTTP url differs from first to last ones
                counter = 0
                for item in sorted(newList):
                    # get playListItemId of item
                    xPathStr = "//" + rootNode + \
                        "[@title='" + newList[item] + "']/@playlistItemID"
                    itemToMove = str(playListXML.xpath(unicode(xPathStr))[0])
                    if counter == 0:
                        url = misc.GetLoopBack() + '/playlists/' + playlistId + \
                            '/items/' + itemToMove + '/move'
                        counter += 1
                        after = itemToMove
                    else:
                        url = misc.GetLoopBack() + '/playlists/' + playlistId + \
                            '/items/' + itemToMove + \
                            '/move?after=' + after
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
                        map(str, (playlist.get('title') for playlist in playlists)))
            for titleInPlayList in playlists.split(','):
                if title == titleInPlayList:
                    return True
            return False

        ''' Import a playlist '''
        def doImport(jsonItems, playlistType, playlistTitle):
           # jsonItems = {}
            playlistSmart = (jsonItems.get('smart') == 1)
            # Make url for creation of playlist
            targetFirstUrl = misc.GetLoopBack() + '/playlists?type=' + playlistType + \
                '&title=' + String.Quote(playlistTitle) + \
                '&smart=0&uri=library://'
            counter = 0
            for lib in jsonItems:
                if counter < 1:
                    targetFirstUrl += lib + '/directory//library/metadata/'
                    medias = ','.join(
                        map(str, (item['id'] for item in jsonItems[lib])))
                    targetFirstUrl += String.Quote(medias)
                    # First url for the post created, so send it, and grab the response
                    try:
                        response = HTTP.Request(
                            targetFirstUrl, cacheTime=0, immediate=True, method="POST")

                        ratingKey = XML.ElementFromString(
                            response).xpath('Playlist/@ratingKey')[0]
                    except Exception, e:
                        Log.Exception(
                            'Exception creating first part of playlist was: %s' % (str(e)))
                    counter += 1
                else:
                    # Remaining as put
                    medias = ','.join(
                        map(str, (item['id'] for item in jsonItems[lib])))
                    targetSecondUrl = misc.GetLoopBack() + '/playlists/' + ratingKey + '/items?uri=library://' + \
                        lib + '/directory//library/metadata/' + \
                        String.Quote(medias)
                    HTTP.Request(targetSecondUrl, cacheTime=0,
                                 immediate=True, method="PUT")
            return ratingKey

        ''' Phrase phrase3Party playlist '''
        def phrase3Party(lines):
            # Placeholder for items to import
            items = {}
            Log.Info('Import file was 3Party')            
            # We need to find out, if this is a regular m3u file, or an extended one            
            if '#EXTM3U' in lines[0].upper():                
                extended = True
                Log.Info('Playlist was an extended one')
            elif '#M3U' in lines[0].upper():                
                extended = False
                Log.Info('Playlist was an non-extended one')
            else:                
                Log.Error('Import file does not start with the line: #EXTM3U or #M3U')
                req.clear()
                req.set_status(406)
                req.finish(
                    'Seems like we are trying to import a file that is not a playlist!')
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
                    Log.Exception('Exception happened in phrase3Party was %s' %(str(e)))
                    pass
                finally:
                    return items
            else:
                
                try:
                    # Guess the media type
                    sType = guessMediaType(lines[2].replace('\r', '').replace('\n', ''))                    
                    # Get possibel libraries to scan
                    libs = getLibsOfType(sType)
                    # Get a key,value list of potential medias   

                    
                    mediaList = getFilesFromLib(libs, sType)


                    
                    return





                    #print 'Ged MediaList', mediaList
                    #Log.Debug('************** PMS contains *****************')
                    #Log.Debug(mediaList)
                    



                    basic = {}
                    counter = 1
                    for line in lines[2:len(lines):3]:
                        basic[str(counter)] = line.replace('\r', '').replace('\n', '')
                        #basic.append(line.replace('\r', '').replace('\n', ''))
                        counter += 1
                    items['basic'] = basic
                    #print 'Ged Basic', basic

                    final = {}

                    for item in basic:
                        #print 'Ged ********', item, basic[item]
                        if basic[item] in mediaList:
                            print 'Ged fundet'
                        else:
                            print 'Ged missed'

                except IndexError:
                    pass
                except Exception, e:
                    Log.Exception('Exception happened in phrase3Party was %s' %(str(e)))
                    pass
                finally:
                    #print 'Ged own', items
                    return 
                    #return items
                

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
                Log.Exception('Exception happened in phraseOurs was %s' %(str(e)))
                pass
            finally:                
                return [sType, smart, items]

        ''' *************** Main stuff here *********************** '''

        returnResult = {}
        success = []
        failed = []
        # Payload Upload file present?
        if not 'localFile' in req.request.files:
            req.clear()
            req.set_status(412)
            req.finish(
                'Missing upload file parameter named localFile from the payload')
        else:
            localFile = req.request.files['localFile'][0]['body']
        try:
            playlistTitle = req.request.files['localFile'][0]['filename'].rsplit('.')[
                0]
            # Make into seperate lines
            lines = localFile.split('\n')
            # Start by checking if we have a valid playlist file            
            if 'M3U' not in lines[0].upper():            
                Log.Error('Import file does not start with the line: #EXTM3U or #M3U')
                req.clear()
                req.set_status(406)
                req.finish(
                    'Seems like we are trying to import a file that is not a playlist!')
                return
            if alreadyPresent(playlistTitle):
                Log.Error('Playlist %s already exists' % playlistTitle)
                req.clear()
                req.set_status(406)
                req.finish('Aborted, since playlist "%s" already existed' % playlistTitle)
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
                    if result != None:
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

    ''' This metode will copy a playlist. between users '''
    @classmethod
    def COPY(self, req, *args):
        users = None
        # Start by getting the key of the PlayList
        if args != None:
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
            else:
                # Copy from the Owner
                userfrom = None
            # Get UserTo
            if 'userto' in arguments:
                # Get the userto
                userto = arguments[arguments.index('userto') + 1]
            else:
                Log.Error('Missing target user of playlist')
                req.clear()
                req.set_status(412)
                req.finish('Missing targetuser of playlist')
            # Get user list, among with access token
            users = plexTV().getUserList()
            # Get the playlist that needs to be copied
            url = misc.GetLoopBack() + '/playlists/' + key + '/items'
            if userfrom == None:
                # Get it from the owner
                playlist = XML.ElementFromURL(url)
            else:
                # We need to logon as specified user
                try:
                    # Get user playlist
                    # TODO Change to native framework call, when Plex allows token in header
                    opener = urllib2.build_opener(urllib2.HTTPHandler)
                    request = urllib2.Request(url)
                    request.add_header(
                        'X-Plex-Token', users[userfrom]['accessToken'])
                    response = opener.open(request).read()
                    playlist = XML.ElementFromString(response)
                except Ex.HTTPError, e:
                    Log.Exception(
                        'HTTP exception  when downloading a playlist for the owner was: %s' % (e))
                    req.clear()
                    req.set_status(e.code)
                    req.finish(str(e))
                except Exception, e:
                    Log.Exception(
                        'Exception happened when downloading a playlist for the user was: %s' % (str(e)))
                    req.clear()
                    req.set_status(500)
                    req.finish(
                        'Exception happened when downloading a playlist for the user was: %s' % (str(e)))
            # Now walk the playlist, and do a lookup for the items, in order to grab the librarySectionUUID
            jsonItems = {}
            playlistType = playlist.get('playlistType')
            playlistTitle = playlist.get('title')
            playlistSmart = (playlist.get('smart') == 1)
            for item in playlist:
                itemKey = item.get('ratingKey')
                xmlUrl = misc.GetLoopBack() + '/library/metadata/' + itemKey + '?' + EXCLUDE
                UUID = XML.ElementFromURL(
                    misc.GetLoopBack() + '/library/metadata/' + itemKey).get('librarySectionUUID')
                if UUID in jsonItems:
                    jsonItems[UUID].append(itemKey)
                else:
                    jsonItems[UUID] = []
                    jsonItems[UUID].append(itemKey)
            Log.Debug('Got a playlist that looks like:')
            Log.Debug(json.dumps(jsonItems))
            # So we got all the info needed now from the source user, now time for the target user
            try:
                # TODO Change to native framework call, when Plex allows token in header
                urltoPlayLists = misc.GetLoopBack() + '/playlists'
                opener = urllib2.build_opener(urllib2.HTTPHandler)
                request = urllib2.Request(urltoPlayLists)
                request.add_header(
                    'X-Plex-Token', users[userto]['accessToken'])
                response = opener.open(request).read()
                playlistto = XML.ElementFromString(response)
            except Ex.HTTPError, e:
                Log.Exception(
                    'HTTP exception when downloading a playlist for the owner was: %s' % (e))
                req.clear()
                req.set_status(e.code)
                req.finish(str(e))
            except Exception, e:
                Log.Exception(
                    'Exception happened when downloading a playlist for the user was: %s' % (str(e)))
                req.clear()
                req.set_status(500)
                req.finish(
                    'Exception happened when downloading a playlist for the user was: %s' % (str(e)))
            # So we got the target users list of playlists, and if the one we need to copy already is there, we delete it
            for itemto in playlistto:
                if playlistTitle == itemto.get('title'):
                    keyto = itemto.get('ratingKey')
                    deletePlayLIstforUsr(
                        req, keyto, users[userto]['accessToken'])
            # Make url for creation of playlist
            targetFirstUrl = misc.GetLoopBack() + '/playlists?type=' + playlistType + \
                '&title=' + String.Quote(playlistTitle) + \
                '&smart=0&uri=library://'
            counter = 0
            for lib in jsonItems:
                if counter < 1:
                    targetFirstUrl += lib + '/directory//library/metadata/'
                    medias = ','.join(map(str, jsonItems[lib]))
                    targetFirstUrl += String.Quote(medias)
                    # First url for the post created, so send it, and grab the response
                    try:
                        opener = urllib2.build_opener(urllib2.HTTPHandler)
                        request = urllib2.Request(targetFirstUrl)
                        request.add_header(
                            'X-Plex-Token', users[userto]['accessToken'])
                        request.get_method = lambda: 'POST'
                        response = opener.open(request).read()
                        ratingKey = XML.ElementFromString(
                            response).xpath('Playlist/@ratingKey')[0]
                    except Exception, e:
                        Log.Exception(
                            'Exception creating first part of playlist was: %s' % (str(e)))
                    counter += 1
                else:
                    # Remaining as put
                    medias = ','.join(map(str, jsonItems[lib]))
                    targetSecondUrl = misc.GetLoopBack() + '/playlists/' + ratingKey + '/items?uri=library://' + \
                        lib + '/directory//library/metadata/' + \
                        String.Quote(medias)
                    opener = urllib2.build_opener(urllib2.HTTPHandler)
                    request = urllib2.Request(targetSecondUrl)
                    request.add_header(
                        'X-Plex-Token', users[userto]['accessToken'])
                    request.get_method = lambda: 'PUT'
                    opener.open(request)
        else:
            Log.Critical('Missing Arguments')
            req.clear()
            req.set_status(412)
            req.finish('Missing Arguments')

    ''' This metode will download a playlist. accepts a user parameter '''
    @classmethod
    def DOWNLOAD(self, req, *args):
        try:
            user = None
            if args != None:
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
                    url = misc.GetLoopBack() + '/playlists/' + key + '/items' + '?' + EXCLUDE
                else:
                    Log.Error('Missing key of playlist')
                    req.clear()
                    req.set_status(412)
                    req.finish('Missing key of playlist')
                try:
                    Log.Info('downloading playlist with ID: %s' % key)     
                    try:
                        title, playList = getPlayListItems( user, key)
                        # Replace invalid caracters for a filename with underscore
                        fileName = re.sub('[\/[:#*?"<>|]', '_',title).strip() + '.m3u8'
                        req.set_header('Content-Disposition','attachment; filename="' + fileName + '"')
                        req.set_header('Cache-Control', 'no-cache')
                        req.set_header('Pragma', 'no-cache')
                        req.set_header('Content-Type', 'application/text/plain')
                        # start writing
                        for line in playList:
                            #print line
                            req.write(unicode(line))
                        req.set_status(200)
                        req.finish()
                    except Exception, e:
                        Log.Exception('Exception when downloading a playlist as the owner was %s' %str(e))
                        Log.Debug('Trying to get more info here')
                        req.clear()
                        req.set_status(500)
                        req.finish(str(e))
                except Ex.HTTPError, e:
                    Log.Exception(
                        'HTTP exception  when downloading a playlist for the owner was: %s' % (e))
                    req.clear()
                    req.set_status(500)
                    req.finish(str(e))
                except Exception, e:
                    Log.Exception(
                        'Exception happened when downloading a playlist for the owner was: %s' % (str(e)))
                    req.clear()
                    req.set_status(500)
                    req.finish(
                        'Exception happened when downloading a playlist for the owner was: %s' % (str(e)))
        except Exception, e:
            Log.Exception(
                'Fatal error happened in playlists.download: ' + str(e))
            req.clear()
            req.set_status(500)
            req.finish(
                'Fatal error happened in playlists.download: %s' % (str(e)))

    ''' This metode will delete a playlist. accepts a user parameter '''
    @classmethod
    def DELETE(self, req, *args):
        try:
            user = None
            if args != None:
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
            if user == None:
                try:
                    # Delete playlist from the owner
                    Log.Info('Deleting playlist with ID: %s' % key)
                    HTTP.Request(url, cacheTime=0,
                                 immediate=True, method="DELETE")
                except Ex.HTTPError, e:
                    Log.Exception(
                        'HTTP exception  when deleting a playlist for the owner was: %s' % (e))
                    req.clear()
                    req.set_status(e.code)
                    req.finish(str(e))
                except Exception, e:
                    Log.Exception(
                        'Exception happened when deleting a playlist for the owner was: %s' % (str(e)))
                    req.clear()
                    req.set_status(500)
                    req.finish(
                        'Exception happened when deleting a playlist for the owner was: %s' % (str(e)))
            else:
                # We need to logon as a user in order to nuke the playlist
                try:
                    # Get user list, among with their access tokens
                    users = plexTV().getUserList()
                    # Detele the playlist
                    deletePlayLIstforUsr(req, key, users[user]['accessToken'])
                except Ex.HTTPError, e:
                    Log.Exception(
                        'HTTP exception  when deleting a playlist for the owner was: %s' % (e))
                    req.clear()
                    req.set_status(e.code)
                    req.finish(str(e))
                except Exception, e:
                    Log.Exception(
                        'Exception happened when deleting a playlist for the user was: %s' % (str(e)))
                    req.clear()
                    req.set_status(500)
                    req.finish(
                        'Exception happened when deleting a playlist for the user was: %s' % (str(e)))
        except Exception, e:
            Log.Exception(
                'Fatal error happened in playlists.delete: ' + str(e))
            req.clear()
            req.set_status(500)
            req.finish(
                'Fatal error happened in playlists.delete: %s' % (str(e)))

    ''' This metode will return a list of playlists. accepts a user parameter '''
    @classmethod
    def LIST(self, req, *args):
        try:
            user = None
            if args != None:
                # We got additional arguments
                if len(args) > 0:
                    # Get them in lower case
                    arguments = [item.lower() for item in list(args)[0]]
                    if 'user' in arguments:
                        # Get key of the user
                        user = arguments[arguments.index('user') + 1]
            # So now user is either none or a keyId
            if user == None:
                playlists = XML.ElementFromURL(self.getListsURL)
            else:
                # Darn....Hard work ahead..We have to logon as another user here :-(
                users = plexTV().getUserList()
                myHeader = {}
                myHeader['X-Plex-Token'] = users[user]['accessToken']
                # TODO Change to native framework call, when Plex allows token in header
                request = urllib2.Request(self.getListsURL, headers=myHeader)
                playlists = XML.ElementFromString(
                    urllib2.urlopen(request).read())
                # playlists = XML.ElementFromURL(self.getListsURL, headers=myHeader)
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


#************************ Internal functions ************************

def deletePlayLIstforUsr(req, key, token):
    url = misc.GetLoopBack() + '/playlists/' + key
    try:
        # TODO Change to native framework call, when Plex allows token in header
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        request = urllib2.Request(url)
        request.add_header('X-Plex-Token', token)
        request.get_method = lambda: 'DELETE'
        url = opener.open(request)
    except Ex.HTTPError, e:
        Log.Exception(
            'HTTP exception  when deleting a playlist for the owner was: %s' % (e))
        req.clear()
        req.set_status(e.code)
        req.finish(str(e))
    except Exception, e:
        Log.Exception(
            'Exception happened when deleting a playlist for the user was: %s' % (str(e)))
        req.clear()
        req.set_status(500)
        req.finish(
            'Exception happened when deleting a playlist for the user was: %s' % (str(e)))
    return req


''' This function returns true or false, if key/path matches for a media '''


def checkItemIsValid(key, title, sType):
    url = misc.GetLoopBack() + '/library/metadata/' + str(key) + '?' + EXCLUDE
    mediaTitle = None
    try:
        mediaTitle = XML.ElementFromURL(url).xpath(
            '//' + ROOTNODES[sType])[0].get('title')
    except:
        pass
    return (title == mediaTitle)

''' This function will search for a a media based on title and type, and return the key '''


def searchForItemKey(title, sType):
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


''' Here we detect the Plex type of a media file '''

def guessMediaType(fileName):
    sType = None
    # Get ext of the file
    ext = os.path.splitext(fileName)[1][1:]    
    for mediaType in VALIDEXT:        
        if ext in VALIDEXT[mediaType]:
            sType = mediaType
    return sType


''' Get libraries of a certain type '''

def getLibsOfType(sType):   
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
        Log.Info('Need to serch the following libraries: %s' %str(libsToSearch))        
        return libsToSearch
    except Exception, e:        
        Log.Exception('Exception in playList getLibsOfType was %s' %str(e))
    return

''' Get media files from filePath '''
def getFilesFromLib(libs, sType):                
    itemList = {}
    # Add from one library at a time
    for lib in libs:        
        start = 0 # Start point of items                
        baseUrl = misc.GetLoopBack() + '/library/sections/' + lib + '/all?type=' + str(MEDIATYPES[ROOTNODES[sType]]) + '&' + EXCLUDE + '&X-Plex-Container-Start='        
        url = baseUrl + '0' + '&X-Plex-Container-Size=0'        
        libInfo = XML.ElementFromURL(url)
        # Now get the amount of items we need to add
        totalSize = libInfo.get('totalSize')
        # Now get the UUID of the library
        librarySectionUUID = libInfo.get('librarySectionUUID')        
        try:
            while int(start) < int(totalSize):                
                url = baseUrl + str(start) + '&X-Plex-Container-Size=' + str(MEDIASTEPS)
                medias = XML.ElementFromURL(url)
                for media in medias:
                    parts = media.xpath('//Media/Part')
                    for part in parts: 
                        mediaInfo = {}                        
                        item = {}
                        mediaInfo = {'fullFileName' : part.get('file'), 'librarySectionUUID' : librarySectionUUID}
                        key = media.get('ratingKey')
                        item[key] = [mediaInfo]
                        itemList[os.path.basename(part.get('file'))] = item                       
                start += MEDIASTEPS                            
        except Exception, e:            
            Log.Exception('exception in getFilesFromLib was: %s' %str(e))
    
    Log.Debug('******** getFilesFromLib **********')
    Log.Debug(itemList)    
    return itemList

'''
getPlayListItems returns an array with the playlist items
Params:
user : key of user, or null if the owner
key : key of playlist
'''
def getPlayListItems(user, key):

    # Send the request to the server, and returns the respond
    def sendReq(userToken, url):
        if not userToken:
            # User is the owner
            try:
                return XML.ElementFromURL(url)
            except Exception, e:
                Log.Exception('Exception when getting a response for %s as the owner was %s' %(url, str(e)))
                return None
        else:
            try:
                # TODO Change to native framework call, when Plex allows token in header
                opener = urllib2.build_opener(urllib2.HTTPHandler)
                request = urllib2.Request(sizeURL)
                request.add_header(
                    'X-Plex-Token', userToken)
                response = opener.open(request).read()
                return XML.ElementFromString(response)
            except Exception, e:
                Log.Exception('Exception when getting a response for %s as a user was %s' %(url, str(e)))
                return None

    # *********** MAIN *****************
    Log.Info('Starting getPlaylistItems with user: %s and key of: %s' %(user, key))
    playlist = []    
    infoURL = misc.GetLoopBack() + '/playlists/' + key
    userToken = None
    if user:        
        # Shared or Home user
        try:
            # Get user list, among with their access tokens
            users = plexTV().getUserList()
            userToken = users[user]['accessToken']
            # TODO Change to native framework call, when Plex allows token in header            
        except Exception, e:
            Log.Exception('Exception getting the token for a user was: %s' %str(e))
            return None
    try:        
        info = sendReq(userToken, infoURL).xpath('//Playlist')[0]        
    except Exception, e:
        Log.Exception('Exception getting info was: %s' %str(e))
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
            content = content[content.index('library', content.index('library')+1):]
        jsonLine["content"] = content
        playListType = info.get('playlistType')
        jsonLine["playlistType"] = playListType
        jsonLine["ServerID"] = XML.ElementFromURL(misc.GetLoopBack() + '/identity').get('machineIdentifier')
        Log.Debug('getPlayListItems returning: %s' %str(jsonLine))
        # Switch to double quotes, to make framework happy
        jsonLine = json.dumps(jsonLine)
        playlist.append(unicode("#" + str(jsonLine) + "\n" ))
        playlist.append("#\n#\n")            
    except Exception, e:
        Log.Exception('Exception in Download was %s' %str(e))
        return None
    start = 0
    while True:        
        url = misc.GetLoopBack() + '/playlists/' + key + '/items?X-Plex-Container-Start=' + str(start) + '&X-Plex-Container-Size=' + str(MEDIASTEPS)
        response = sendReq(userToken, url)        
        start += MEDIASTEPS        
        if response.get('size') == '0':
            break
        try:
            root = '//' + ROOTNODES[playListType]            
            for item in response.xpath(root):                
                # Get the Library UUID
                itemURL = misc.GetLoopBack() + '/library/metadata/' + item.get('ratingKey') + '?' + EXCLUDE            
                libraryUUID = sendReq(userToken, itemURL).get('librarySectionUUID')
                playlist.append(unicode('#{"Id":' + item.get('ratingKey') + ', "ListId":' + str(item.get('playlistItemID')) + ', "LibraryUUID":"' + libraryUUID + '"}\n'))
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
                        if item.get('originalTitle') == None:
                            row = row + item.get('grandparentTitle').replace(
                                ' - ', ' ') + ' - ' + item.get('title').replace(' - ', ' ')
                        else:
                            row = row + item.get('originalTitle').replace(
                                ' - ', ' ') + ' - ' + item.get('title').replace(' - ', ' ')
                    except Exception, e:
                        Log.Exception(
                            'Exception digesting an audio entry was %s' % (str(e)))
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
                            'Exception happened when digesting the line for Playlist was %s' % (str(e)))
                        pass
                # Pictures
                else:
                    row = row + 'Picture - ' + \
                        item.get('title').replace(' - ', ' ')
                playlist.append(unicode(row + '\n'))                    
                # Add file path
                playlist.append(unicode(item.xpath('Media/Part/@file')[0]) + '\n') 
        except Exception, e:                
            Log.Exception('Exception in getPlayListItems was: %s' %str(e))
            Log.Critical('Url to offending item was %s' %itemURL) 
            return None                                                  
    return [ title, playlist ]

