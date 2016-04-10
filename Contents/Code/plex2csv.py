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
		else:
			req.clear()
			req.set_status(412)
			req.finish("Unknown function call")

	''' This will return a list of fields avail
			Param needed is type=[movie,show,audio,picture]
	'''
	def getFields(self, req):
		print 'Ged her'
		type = req.get_argument('type', 'missing')
		if type == 'missing':
			req.clear()
			req.set_status(412)
			req.finish("Missing type parameter")
		return

