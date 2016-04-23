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
			# Call scanSection
			return self.getFields(req)
		elif function == 'getFieldListbyIdx':
			# Call scanSection
			return self.getFieldListbyIdx(req)
		else:
			req.clear()
			req.set_status(412)
			req.finish("Unknown function call")

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
		if type=='movie':
			getMovieListbyIdx(req)



	''' This will return a list of fields avail
			Param needed is type=[movie,show,audio,picture]
	'''
	def getFields(self, req):
		def getFullMovieFieldsList(req):
			print 'Ged 1'
			req.clear()
			req.set_status(200)
			req.finish(json.dumps(plex2csv_moviefields.fields))
					
		type = req.get_argument('type', 'missing')
		if type == 'missing':
			req.clear()
			req.set_status(412)
			req.finish("Missing type parameter")
		if type=='movie':
			getFullMovieFieldsList(req)



