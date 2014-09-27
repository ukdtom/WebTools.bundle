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
PLUGIN_VERSION = '0.0.0.1'
PREFIX = '/utils/webtools'
NAME = 'WebTools'
ART  = 'art-default.jpg'
ICON = 'icon-default.png'

#********** Imports needed *********
import os
from subprocess import call

#********** Initialize *********
def Start():
	print("********  Started %s on %s  **********" %(NAME  + ' V' + PLUGIN_VERSION, Platform.OS))
	Log.Debug("*******  Started %s on %s  ***********" %(NAME + ' V' + PLUGIN_VERSION, Platform.OS))
	HTTP.CacheTime = 0
	ObjectContainer.art = R(ART)
	DirectoryObject.thumb = R(ICON)
	ObjectContainer.title1 = NAME + '...(If running on Web Client, go to http://<PMS>:32400/web/' + NAME + '/index.html instead)' 
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
def MainMenu(Func='', **kwargs):
	if Func=='':
		Log.Debug("***** Called from Channel view, so do std. channel stuff here ******")



