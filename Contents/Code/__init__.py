######################################################################################################################
#					WebTools bundle for Plex
#
#					Allows you to manipulate subtitles on Plex Media Server
#
#					Author:			dagaluf, a Plex Community member
#					Author:			dane22, a Plex Community member
#
#					Support thread:	https://forums.plex.tv/index.php/topic/119940-webtool-subtitle-manager-development/
#
######################################################################################################################

#********* Constants used **********
PLUGIN_VERSION = '0.0.0.2'
PREFIX = '/utils/webtools'
NAME = 'WebTools'
ART  = 'art-default.jpg'
ICON = 'icon-default.png'
MYSECRET = 'BarkleyIsAFineDog'

#********** Imports needed *********
import os, io
from subprocess import call

#********** Initialize *********
def Start():
	print("********  Started %s on %s  **********" %(NAME  + ' V' + PLUGIN_VERSION, Platform.OS))
	Log.Debug("*******  Started %s on %s  ***********" %(NAME + ' V' + PLUGIN_VERSION, Platform.OS))
	HTTP.CacheTime = 0
	ObjectContainer.art = R(ART)
	DirectoryObject.thumb = R(ICON)
	ObjectContainer.title1 = NAME + ' V' + PLUGIN_VERSION 
	Plugin.AddViewGroup('List', viewMode='List', mediaType='items')
	ObjectContainer.view_group = 'List'
	setupSymbLink()

#********** Create Website *********
''' Create symbolic links in the WebClient, so we can access this bundle frontend via a browser directly '''
@route(PREFIX + '/setup')
def setupSymbLink():
	src = Core.storage.join_path(Core.app_support_path, 'Plug-ins', NAME + '.bundle', 'http')
	dst = Core.storage.join_path(Core.app_support_path, 'Plug-ins', 'WebClient.bundle', 'Contents', 'Resources', NAME)
	if not os.path.lexists(dst):
		if Platform.OS=='Windows':
			Log.Debug('Darn ' + Platform.OS)
			# Cant create a symb link on Windows, until Plex moves to Python 3.3
			#call(["C:\Users\TM\AppData\Local\Plex Media Server\Plug-ins\WebTools.bundle\RightClick_Me_And_Select_Run_As_Administrator.cmd"])
		else:

		# This creates a symbolic link for the bundle in the WebClient.
		# URL is http://<IP of PMS>:32400/web/WebTools/index.html
			os.symlink(src, dst)
			Log.Debug("SymbLink not there, so creating %s pointing towards %s" %(dst, src))
	else:
		Log.Debug("SymbLink already present")

#********** Main function *********
''' Main menu '''
@handler(PREFIX, NAME, ICON, ART)
@route(PREFIX + '/MainMenu')
def MainMenu(Func='', **kwargs):	
	if Func=='':
		Log.Debug("**********  Starting MainMenu  **********")	
		oc = ObjectContainer()
		if setPMSPath():
			oc.add(DirectoryObject(key=Callback(MainMenu), title="To access this channel, go to"))
			oc.add(DirectoryObject(key=Callback(MainMenu), title='http://<PMS>:32400/web/' + NAME + '/index.html'))
		else:
			oc.add(DirectoryObject(key=Callback(MainMenu), title="Bad or missing settings"))	
			oc.add(DirectoryObject(key=Callback(MainMenu), title="Select Preferences to set ip address of the PMS"))
			oc.add(DirectoryObject(key=Callback(MainMenu), title="Afterwards, refresh this page"))
		oc.add(PrefsObject(title='Preferences', thumb=R('icon-prefs.png')))
		Log.Debug("**********  Ending MainMenu  **********")
		return oc

####################################################################################################
# Set PMS Path
####################################################################################################
@route(PREFIX + '/setPMSPath')
def setPMSPath():
	Log.Debug('Entering setPMSPath')
	# Let's check if the PMS path is valid
	myPath = Prefs['PMS_Path']
	Log.Debug('My master set the Export path to: %s' %(myPath))
	try:
		#Let's see if we can add out subdirectory below this
		tmpTest = XML.ElementFromURL('http://' + myPath + ':32400')
		return True		
	except:
		Log.Critical('Bad pmsPath')
		return False

####################################################################################################
# ValidatePrefs
####################################################################################################
@route(PREFIX + '/ValidatePrefs')
def ValidatePrefs():
	if setPMSPath():
		Log.Debug('Prefs are valid, so lets update the js file')
		myFile = os.path.join(Core.app_support_path, 'Plug-ins', NAME + '.bundle', 'http', 'javascript', 'functions.js')
		global MYSECRET 
		MYSECRET = Hash.MD5(Prefs['PMS_Path'])
		print MYSECRET
		with io.open(myFile) as fin, io.open(myFile + '.tmp', 'w') as fout:
			for line in fin:
				if 'var Secret =' in line:
					line = 'var Secret = ' + MYSECRET + ';\n'
				elif 'var PMSUrl =' in line:
					line = 'var PMSUrl = ' + Prefs['PMS_Path'] + ';\n'					
				fout.write(unicode(line))
		os.rename(myFile, myFile + '.org')
		os.rename(myFile + '.tmp', myFile)
	return

