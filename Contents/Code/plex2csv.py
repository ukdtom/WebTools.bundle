######################################################################################################################
#	Plex2CSV module unit
#
#	Author: dane22, a Plex Community member
#
# NAME variable must be defined in the calling unit, and is the name of the application
#
# This module is the main module for Plex2CSV
#
######################################################################################################################

import plex2csv_moviefields
import json


class plex2csv(object):
    # Defaults used by the rest of the class
    def __init__(self):
        return

    ''' Grap the tornado req, and process it '''

    def reqprocess(self, req):
        function = req.get_argument('function', 'missing')
        if function == 'missing':
            req.clear()
            req.set_status(412)
            req.finish("Missing function parameter")
        elif function == 'getFields':
            # Call getFields
            return self.getFields(req)
        elif function == 'getFieldListbyIdx':
            # Call getFieldListbyIdx
            return self.getFieldListbyIdx(req)
        elif function == 'getDefaultLevels':
            # Call getDefaultLevels
            return self.getDefaultLevels(req)
        else:
            req.clear()
            req.set_status(412)
            req.finish("Unknown function call")

    '''	Returns a jason with the build-in levels
			Param needed is type=[movie,show,audio,picture]
	'''

    def getDefaultLevels(self, req):
        def getMovieDefLevels(req):
            myResult = []
            fields = json.dumps(
                plex2csv_moviefields.movieDefaultLevels, sort_keys=True)
            print 'Ged1', fields
            print 'Ged2'
            for key, value in fields:
                print 'Ged2', key
                myResult.append(key)
            req.clear()
            req.set_status(200)
            req.finish(json.dumps(myResult))

        # Main code
        type = req.get_argument('type', 'missing')
        if type == 'missing':
            req.clear()
            req.set_status(412)
            req.finish("Missing type parameter")
        if type == 'movie':
            getMovieDefLevels(req)

    ''' Returns an array of possible fields for a section type.
			Param needed is type=[movie,show,audio,picture]
	'''

    def getFieldListbyIdx(self, req):
        def getMovieListbyIdx(req):
            req.clear()
            req.set_status(200)
            req.finish(json.dumps(plex2csv_moviefields.fieldsbyID))

        # Main code
        type = req.get_argument('type', 'missing')
        if type == 'missing':
            req.clear()
            req.set_status(412)
            req.finish("Missing type parameter")
        if type == 'movie':
            getMovieListbyIdx(req)

    ''' This will return a list of fields avail
			Param needed is type=[movie,show,audio,picture]
	'''

    def getFields(self, req):
        def getFullMovieFieldsList(req):
            req.clear()
            req.set_status(200)
            req.finish(json.dumps(plex2csv_moviefields.fields))

        # Main code
        type = req.get_argument('type', 'missing')
        if type == 'missing':
            req.clear()
            req.set_status(412)
            req.finish("Missing type parameter")
        if type == 'movie':
            getFullMovieFieldsList(req)
