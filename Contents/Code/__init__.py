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
PLUGIN_VERSION = '0.0.0.3'
PREFIX = '/utils/webtools'
NAME = 'WebTools'
ART  = 'art-default.jpg'
ICON = 'icon-default.png'
MYSECRET = 'BarkleyIsAFineDog'
ERRORAUTH = 'Error authenticating'

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
def MainMenu(Func='', Secret='', **kwargs):
	if Func=='':
		Log.Debug("**********  Starting MainMenu  **********")	
		oc = ObjectContainer()
		if setPMSPath():
			oc.add(DirectoryObject(key=Callback(MainMenu), title="To access this channel, go to"))
			oc.add(DirectoryObject(key=Callback(MainMenu), title='http://' + Prefs['PMS_Path'] + ':32400/web/' + NAME + '/index.html'))
		else:
			oc.add(DirectoryObject(key=Callback(MainMenu), title="Bad or missing settings"))	
			oc.add(DirectoryObject(key=Callback(MainMenu), title="Select Preferences to set ip address of the PMS"))
			oc.add(DirectoryObject(key=Callback(MainMenu), title="Afterwards, refresh this page"))
		oc.add(PrefsObject(title='Preferences', thumb=R('icon-prefs.png')))
		Log.Debug("**********  Ending MainMenu  **********")
		return oc
	# Here comes the functions avail
	elif Func=='PathExists':
		return PathExists(Secret, kwargs.get("Path"))
	elif Func=='ShowSRT':
		return ShowSRT(Secret, kwargs.get("FileName"))
	elif Func=='DelSub':
		return DelSub(Secret, kwargs.get("MediaID"), kwargs.get("SubFileID"))
	elif Func=='GetXMLFile':
		return GetXMLFile(Secret, kwargs.get("Path"))

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
		myFile = os.path.join(Core.app_support_path, 'Plug-ins', NAME + '.bundle', 'http', 'jscript', 'functions.js')
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

####################################################################################################
# Check Secret
####################################################################################################
''' Check if the Secret provided is valid
Returns true is okay, and else false '''
@route(PREFIX + '/PwdOK')
def PwdOK(Secret):
	if (Hash.MD5(Prefs['PMS_Path']) == Secret):
		return True
	else:
		return False

####################################################################################################
# Check if a path exists
####################################################################################################
''' Check if a path exists.	Returns true if if it does, else false '''
@route(PREFIX + '/PathExists')
def PathExists(Secret, Path):
	if PwdOK(Secret):		
		# Now we got the filename and dir name, so let's nuke the file
		if os.path.exists(Path):
			return 'true'
		else:
			return 'false'				
	else:
		return ERRORAUTH

####################################################################################################
# Show contents of a txt file
####################################################################################################
''' Show contents of a txt file '''
@route(PREFIX + '/ShowSRT')
def ShowSRT(Secret, FileName):
	if PwdOK(Secret):
		with io.open (FileName, "rb") as myfile:		
			return myfile.read()
	else:
		return ERRORAUTH

####################################################################################################
# Delete a subtitle file
####################################################################################################
''' Delete a subtitle file.	Returns ok if all goes well '''
@route(PREFIX + '/DelSub')
def DelSub(Secret, MediaID, SubFileID):
	if PwdOK(Secret):		
		# Now we got the filename and dir name, so let's nuke the file
		try:			
			Log.Debug('***** Trying to delete the Sub file %s from the media %s *****' %(SubFileID, MediaID))
			myFiles = []
			# Let's start by grapping the media info from it's tree
			myURL = 'http://127.0.0.1:32400/library/metadata/' + MediaID + '/tree'			
			myMediaStreams = XML.ElementFromURL(myURL).xpath('//MediaPart/MediaStream')
			# We got a collection of MediaParts, so start walking them
			for myMediaStream in myMediaStreams:
				if myMediaStream.get('id') == SubFileID:
					# We got the correct sub file
					mySub = myMediaStream.get('url')
					Log.Debug('Sub file found is %s' %(mySub))
					# Okay....Got the agent, now let's find the path to the bundle/contents directory
					myHash = XML.ElementFromURL(myURL).xpath('//MediaPart/@hash')[0]
					# Create a string containing the path to the contents directory
					myPath = os.path.join(Core.app_support_path, 'Media', 'localhost', myHash[0], myHash[1:]+ '.bundle', 'Contents')
					if 'media://' in mySub:
						# Let's find the agent in spe, and start by getting LangCode/Agent
						import re
						try:
							myAgent = re.search('Contents/Subtitles/(.*)', mySub).group(1)					
						except:
							Log.Debug('Error digesting string %s' %(mySub))		
						# Now seperate the lang code
						lang, myAgent = myAgent.split("/")
						# Let's get the filename
						mySubFile = myAgent							
						realAgentName, realSubFile = myAgent.split('_')
						# The result for the subtitles contribution folder						
						realSubPathForSubCont = os.path.join(myPath, 'Subtitle Contributions', realAgentName, lang, realSubFile)
						# The result for the Symbolic links
						realPathForSymbLink = os.path.join(myPath, 'Subtitles', lang, myAgent)
						# Add to array of files to delete
						myFiles.append(realSubPathForSubCont)
						myFiles.append(realPathForSymbLink)						
					else:
						realAgentName = 'com.plexapp.agents.localmedia'
						mySubFile = mySub[7:]
						myFiles.append(mySubFile)
					for myFile in myFiles:
						Log.Debug('Delete %s' %(myFile))
						os.remove(myFile)						
					# XML files that we need to manipulate
					xmlFile1 = os.path.join(myPath, 'Subtitles.xml')
					xmlFile2 = os.path.join(myPath, 'Subtitle Contributions',  realAgentName + '.xml')
					if (realAgentName!='com.plexapp.agents.localmedia'):
						DelFromXML(xmlFile2, 'media', realSubFile)
						DelFromXML(xmlFile1, 'media', realSubFile)
					else:
						DelFromXML(xmlFile2, 'file', mySubFile)
						DelFromXML(xmlFile1, 'file', mySubFile)
					break
			Log.Debug('***** DelSub ended okay *****')
			return 'ok'				
		except OSError:
			return 'error'
	else:
		return ERRORAUTH

####################################################################################################
# Delete from an XML file
####################################################################################################
''' Delete from an XML file '''
@route(PREFIX + '/DelFromXML')
def DelFromXML(fileName, attribute, value):
	Log.Debug('Need to delete element with an attribute named "%s" with a value of "%s" from file named "%s"' %(attribute, value, fileName))
	from xml.etree import ElementTree
	with io.open(fileName, 'r') as f:
		tree = ElementTree.parse(f)
		root = tree.getroot()
		mySubtitles = root.findall('.//Subtitle')
		for Subtitles in root.findall("Language[Subtitle]"):
			for node in Subtitles.findall("Subtitle"):
				myValue = node.attrib.get(attribute)
				if myValue:
					if '_' in myValue:
						drop, myValue = myValue.split("_")
					if myValue == value:
						Subtitles.remove(node)
	tree.write(fileName, encoding='utf-8', xml_declaration=True)
	return

####################################################################################################
# Returns the contents of an XML file
####################################################################################################
''' Returns the contents of an XML file '''
@route(PREFIX + '/GetXMLFile')
def GetXMLFile(Secret, Path):
	if PwdOK(Secret):
		Log.Debug('Getting contents of an XML file named %s' %(Path))
		document = et.parse( Path )
		root = document.getroot()
		return et.tostring(root, encoding='utf8', method='xml')
	else:
		return ERRORAUTH

