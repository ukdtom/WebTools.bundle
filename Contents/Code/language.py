######################################################################################################################
#	Language helper unit					
#
#	Author: dane22, a Plex Community member
#
# This unit works with supported languages within Plex
#
# NAME variable must be defined in the calling unit, and is the name of the application
#
######################################################################################################################

import json, sys

class language(object):
	# Defaults used by the rest of the class
	def __init__(self):
		return

	''' Grap the tornado req, and process it for a GET request'''
	def reqprocess(self, req):		
		function = req.get_argument('function', 'missing')
		if function == 'missing':
			req.clear()
			req.set_status(412)
			req.finish('Missing function parameter')
		elif function == 'getCountryCodes':
			return self.getCountryCodes(req)
		elif function == 'getMatch':
			return self.getMatch(req)
		elif function == 'getLangCodeList':
			return self.getLangCodeList(req)
		elif function == 'getCodeLangList':
			return self.getCodeLangList(req)
		else:
			req.clear()
			req.set_status(412)
			req.finish('Unknown function call')

	''' Returns an array of valid country codes '''
	def getCountryCodes(self, req):
		req.clear()
		req.set_status(200)
		req.finish(json.dumps(Locale.Language.All()))

	''' Here we return a valid country code, based on the language param '''
	def getMatch(self, req):
		code = req.get_argument('language', 'missing')
		if code == 'missing':
			req.clear()
			req.set_status(412)
			req.finish('Missing language parameter')
		# Match the code
		req.clear()
		req.set_status(200)
		req.finish(json.dumps(Locale.Language.Match(code)))

	''' Here we return an ordered jason of language:countrycode for all the valid ones '''
	def getLangCodeList(self, req):
		# Walk the darn module
		all_languages = {}
		cls = dir(Locale.Language)
		for name in cls:
			if name[0] != '_':
				if name not in ['All', 'Match', 'lock']:
					code = Locale.Language.Match(name)
					if code != 'xx':
						all_languages[name] = code
		req.clear()
		req.set_status(200)
		req.finish(json.dumps(all_languages, sort_keys=True))

	''' Here we return an ordered jason of countrycode:language for all the valid ones '''
	def getCodeLangList(self, req):
		# Walk the darn module
		all_languages = {}
		cls = dir(Locale.Language)
		for name in cls:
			if name[0] != '_':
				if name not in ['All', 'Match', 'lock']:
					code = Locale.Language.Match(name)
					if code != 'xx':
						all_languages[code] = name
		req.clear()
		req.set_status(200)
		req.finish(json.dumps(all_languages, sort_keys=True))








