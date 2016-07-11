######################################################################################################################
#	Plex2CSV module unit					
#
#	Author: dane22, a Plex Community member
#
# This module is for schedules, if needed
#
######################################################################################################################


#TODO This module is not working yet

import io, os, json


class scheduler(object):
	init_already = False							# Make sure part of init only run once
	# Init of the class
	def __init__(self):

		return

	''' Grap the tornado req, and process it for a GET request'''
	def reqprocess(self, req):
		function = req.get_argument('function', 'missing')
		if function == 'missing':
			req.clear()
			req.set_status(412)
			req.finish("<html><body>Missing function parameter</body></html>")
		elif function == 'getSchedules':
			req.clear()
			req.finish(self.getSchedules(req))
		elif function == 'getSchedule':
			#TODO Add a getSchedule method
			return
		else:
			req.clear()
			req.set_status(412)
			req.finish("<html><body>Unknown function call</body></html>")

	''' Grap the tornado req, and process it for a POST request'''
	def reqprocessPost(self, req):		
		function = req.get_argument('function', 'missing')
		if function == 'missing':
			req.clear()
			req.set_status(412)
			req.finish("<html><body>Missing function parameter</body></html>")
		elif function == 'setSchedule':
			return self.setSchedule(req)
		else:
			req.clear()
			req.set_status(412)
			req.finish("<html><body>Unknown function call</body></html>")

	''' Add a schedule '''
	def setSchedule(self, req):
		print 'Ged setSchedule'
		Log.Info('setSchedule called')
		try:
			name = req.get_argument('name', '_schedule_missing_')
			if name == '_schedule_missing_':
				req.clear()
				req.set_status(412)
				req.finish("<html><body>Missing name parameter</body></html>")
			startTime = req.get_argument('startTime', '_schedule_missing_startTime')
			if startTime == '_schedule_missing_startTime':
				req.clear()
				req.set_status(412)
				req.finish("<html><body>Missing startTime parameter</body></html>")
			repeatHours = req.get_argument('startTime', '_schedule_missing_repeatHours')
			if repeatHours == '_schedule_missing_repeatHours':
				req.clear()
				req.set_status(412)
				req.finish("<html><body>Missing repeatHours parameter</body></html>")
			command = req.get_argument('startTime', '_schedule_missing_command')
			if command == '_schedule_missing_command':
				req.clear()
				req.set_status(412)
				req.finish("<html><body>Missing command parameter</body></html>")
			usePMS = req.get_argument('startTime', '_schedule_missing_usePMS')
			if usePMS == '_schedule_missing_usePMS':
				req.clear()
				req.set_status(412)
				req.finish("<html><body>Missing usePMS parameter</body></html>")



		except Exception, e:
			Log.Exception('Exception in setSchedule' + str(e))






	''' returns a json of scheduled tasks '''
	def getSchedules(self, req):
		# Got any schedules
		if 'schedules' in Dict:
			req.set_status(200)
			return Dict['schedules']
		else:
			req.set_status(404)
			return





