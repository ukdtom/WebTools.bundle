######################################################################################################################
#	NFO Exporter module for WebTools
#
#	Author: dane22, a Plex Community member
#
######################################################################################################################

statusMsg = 'idle'																																									# Response to getStatus
runningState = 0																																										# Internal tracker of where we are
bAbort = False																																											# Flag to set if user wants to cancel

class nfoExporter(object):
	init_already = False							# Make sure init only run once
	bResultPresent = False						# Do we have a result to present

	# Defaults used by the rest of the class
	def __init__(self):
		# Only init once during the lifetime of this
		if not nfoExporter.init_already:
			nfoExporter.init_already = True
			self.populatePrefs()
			Log.Debug('******* Starting nfoExporter *******')

	''' Populate the defaults, if not already there '''
	def populatePrefs(self):
		if Dict['nfoExporter'] == None:
			Dict['nfoExporter'] = {}
			Dict.Save()


	''' Grap the tornado req, and process it for a POST request'''
	def reqprocessPost(self, req):
		function = req.get_argument('function', 'missing')
		if function == 'missing':
			req.clear()
			req.set_status(412)
			req.finish("<html><body>Missing function parameter</body></html>")
		elif function == 'export':
			return self.export(req)
		else:
			req.clear()
			req.set_status(412)
			req.finish("<html><body>Unknown function call</body></html>")

	def export(self, req):

		''' Return the type of the section '''
		def getSectionType(section):
			url = 'http://127.0.0.1:32400/library/sections/' + section + '/all?X-Plex-Container-Start=1&X-Plex-Container-Size=0'
			return XML.ElementFromURL(url).xpath('//MediaContainer/@viewGroup')[0]

		def scanMovieSection(req, section):
			print 'Ged1 scanMovieSection'

		def scanShowSection(req, section):
			print 'Ged1 scanShowSection'	


		# ********** Main function **************
		Log.Info('nfo export called')
		try:
			section = req.get_argument('section', '_export_missing_')
			if section == '_export_missing_':
				req.clear()
				req.set_status(412)
				req.finish("<html><body>Missing section parameter</body></html>")
			if getSectionType(section) == 'movie':
				scanMovieSection(req, section)
			elif getSectionType(section) == 'show':
				scanShowSection(req, section)
			else:
				Log.debug('Unknown section type for section:' + section + ' type: ' + getSectionType(section))
				req.clear()
				req.set_status(404)
				req.finish("Unknown sectiontype")
		except Exception, e:
			Log.Exception('Exception in nfo export' + str(e))







