#########################################################################################################
#				Updater class for Plex Channels
#				Get release info for a git on github.com
#				Author:	dane22, a Plex Community member
#########################################################################################################
#				Usage:
#				- To download info about the latest release for a GitHub Repo:
#					* call getlatestinfo(repo-owner, repo-name, doLog=False)
#							It is STRONGLY recommended not to run this everytime the channel runs,
#							but only at like every 7 days etc.
#							If an error is detected, it'll return False, else an array with the info
#########################################################################################################

import datetime as dt

class updater(object):
	''' Get info regarding latest release from GitHub, and save that in the Dict'''
	def getlatestinfo(self, repoowner, reponame, doLog=False, getAll=False):
		if getAll:
			URL = 'https://api.github.com/repos/' + repoowner + '/' + reponame + '/releases'
		else:
			URL = 'https://api.github.com/repos/' + repoowner + '/' + reponame + '/releases/latest'
		if doLog:
			Log.Info('Got a request to fetch latest release info for url: %s' %(URL))
		try:
			updateJSON = JSON.ObjectFromURL(URL)
			if doLog:
				Log.Debug('Updater got the following:')
				Log.Debug(updateJSON)				
			return updateJSON
		except:
			Log.Critical('An exception happened in getlatestinfo')
			return False
