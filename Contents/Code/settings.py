######################################################################################################################
#	Settings helper unit for WebTools
#
#	Author: dane22, a Plex Community member
#
######################################################################################################################

import json, sys

class settings(object):

	''' Grap the tornado req, and process it for a GET request'''
	def reqprocess(self, req):		
		function = req.get_argument('function', 'missing')
		if function == 'missing':
			req.clear()
			req.set_status(412)
			req.finish("<html><body>Missing function parameter</body></html>")
		elif function == 'getSettings':
			return self.getSettings(req)
		elif function == 'getSetting':
			return self.getSetting(req)
		else:
			req.clear()
			req.set_status(412)
			req.finish("<html><body>Unknown function call</body></html>")

	''' Grap the tornado req, and process it for a PUT request'''
	def reqprocessPUT(self, req):		
		function = req.get_argument('function', 'missing')
		if function == 'missing':
			req.clear()
			req.set_status(412)
			req.finish("<html><body>Missing function parameter</body></html>")
		elif function == 'putSetting':
			return self.putSetting(req)
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
			req.finish("Missing function parameter")
		elif function == 'setPwd':
			return self.setPwd(req)
		else:
			req.clear()
			req.set_status(412)
			req.finish("<html><body>Unknown function call</body></html>")

	# Change the local auth password
	def setPwd(self, req):
		Log.Debug('Recieved a call for setPwd')
		try:
			req.clear()
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			oldPwd = req.get_argument('oldPwd', 'missing')
			if oldPwd == 'missing':
				req.set_status(412)
				req.finish("Missing oldPwd parameter")
			newPwd = req.get_argument('newPwd', 'missing')
			if newPwd == 'missing':
				req.set_status(400)
				req.finish("Missing newPwd parameter")
			else:
				# Does old pwd match?
				if oldPwd == Dict['password']:
					# Save new Pwd
					Dict['password'] = newPwd
					Dict.Save
					req.set_status(200)
					req.finish("Password saved")			
				else:
					req.set_status(401)
					req.finish("Old Password did not match")			
				return req
		except Ex.HTTPError, e:
			Log.Exception('Error in setPwd: ' + str(e))
			req.clear()
			req.set_status(e.code)
			req.finish(str(e))
			return req

	# Return the value of a specific setting
	def putSetting(self, req):
		Log.Debug('Recieved a call for putSetting')
		try:
			req.clear()
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			name = req.get_argument('name', 'missing')
			if name == 'missing':
				req.set_status(412)
				req.finish("<html><body>Missing name parameter</body></html>")
			value = req.get_argument('value', 'missing')
			if value == 'missing':
				req.set_status(412)
				req.finish("<html><body>Missing value parameter</body></html>")
			else:
				Dict[name] = value
				Dict.Save()
				req.set_status(200)
				req.finish("Setting saved")			
			return req
		except Ex.HTTPError, e:
			Log.Exception('Error in putSetting: ' + str(e))
			req.clear()
			req.set_status(e.code)
			req.finish(str(e))


	# Return the value of a specific setting
	def getSetting(self, req):
		Log.Debug('Recieved a call for getSetting')
		try:
			req.clear()
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			name = req.get_argument('name', 'missing')
			if name == 'missing':
				req.set_status(412)
				req.finish("<html><body>Missing name parameter</body></html>")
			else:
				retVal = Dict[name]
				if retVal:
					Log.Debug('Returning %s' %(retVal))
					req.set_status(200)
					req.finish(json.dumps(retVal))
				else:
					Log.Debug('Variable %s not found' %(name))					
					req.set_status(404)
					req.finish(json.dumps('Setting not found'))
				return req
		except Ex.HTTPError, e:
			Log.Exception('Error in getSetting: ' + str(e))
			req.clear()
			req.set_status(e.code)
			req.finish(str(e))


	# Return all settings from the Dict
	def getSettings(self, req):
		Log.Debug('Recieved a call for getSettings')
		try:
			mySetting = {}
			mySetting['options_hide_integrated'] = (Dict['options_hide_integrated'] == 'true')
			mySetting['options_hide_withoutsubs'] = (Dict['options_hide_withoutsubs'] == 'true')
			mySetting['options_hide_local'] = (Dict['options_hide_local'] == 'true')
			mySetting['options_only_multiple'] = (Dict['options_only_multiple'] == 'true')
			mySetting['items_per_page'] = int(Dict['items_per_page'])
			mySetting['debug'] = (Dict['debug'] == 'true')
			Log.Debug('Returning settings as %s' %(mySetting))
			req.clear()
			req.set_status(200)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish(json.dumps(mySetting))
			return req
		except Ex.HTTPError, e:
			Log.Exception('Error in getSettings: ' + str(e))
			req.clear()
			req.set_status(e.code)
			req.finish(str(e))

