#########################################################################################################
#				Updater class for Plex Channels
#				Get release info for a git on github.com
#				Author:	dane22, a Plex Community member
#########################################################################################################
#				Usage:
#				- To download info about the latest release for a GitHub Repo:
#				Parameters needed are:
#					version : current or all
#					owner : Owner of the git
#					repo : Name of the repo
#				like:
#					&version=current?owner=dagalufh?repo=WebTools.bundle
#
#							It is STRONGLY recommended not to run this everytime the channel runs,
#							but only at like every 7 days etc.
#							If an error is detected, it'll return False, else an array with the info
#########################################################################################################

import datetime as dt

class updater(object):
	def reqprocess(self, req):
		function = req.get_argument('function', 'missing')
		if function == 'missing':
			req.clear()
			req.set_status(412)
			req.finish("<html><body>Missing function parameter</body></html>")
		elif function == 'getGit':
			# Check needed params
			version = req.get_argument('version', 'latest')
			owner = req.get_argument('owner', 'missing')
			if owner == 'missing':
				req.clear()
				req.set_status(412)
				req.finish("<html><body>Missing owner parameter</body></html>")
			repo = req.get_argument('repo', 'missing')
			if repo == 'missing':
				req.clear()
				req.set_status(412)
				req.finish("<html><body>Missing repo parameter</body></html>")
			# Grap the info from GitHub
			return self.getlatestinfo(owner, repo, version, True)
		

	''' Get info regarding latest release from GitHub, and save that in the Dict'''
	def getlatestinfo(self, repoowner, reponame, version, doLog=False):
		url = 'https://api.github.com/repos/' + repoowner + '/' + reponame + '/releases'

		print 'GED TM', version

		if version == 'latest':
			print 'Ged only latest'
			url += '/latest'		

		Log.Debug('Starting getlatestinfo with the url: ' + url)
		print 'GED:', url



		print 'GED2223', version


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
