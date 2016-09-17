######################################################################################################################
#	Plex2CSV module unit					
#
#	Author: dane22, a Plex Community member
#
# This module is for misc utils
#
# Path of code here shamelessly stolen from Plex scanner bundle
#
######################################################################################################################

import os, re, string, unicodedata, sys

RE_UNICODE_CONTROL =  u'([\u0000-\u0008\u000b-\u000c\u000e-\u001f\ufffe-\uffff])' + \
                      u'|' + \
                      u'([%s-%s][^%s-%s])|([^%s-%s][%s-%s])|([%s-%s]$)|(^[%s-%s])' % \
                      (
                        unichr(0xd800),unichr(0xdbff),unichr(0xdc00),unichr(0xdfff),
                        unichr(0xd800),unichr(0xdbff),unichr(0xdc00),unichr(0xdfff),
                        unichr(0xd800),unichr(0xdbff),unichr(0xdc00),unichr(0xdfff)
                      )



class misc(object):	
	init_already = False							# Make sure part of init only run once
	# Init of the class
	def __init__(self):
		return

	''' Below function shamefully stolen from the scanner.bundle, yet modified a bit '''
	# Safely return Unicode.
	def Unicodize(self, s):
		# Precompose.
		try: s = unicodedata.normalize('NFKC', s.decode('utf-8'))
		except:
		  try: s = unicodedata.normalize('NFKC', s.decode(sys.getdefaultencoding()))
		  except:
		    try: s = unicodedata.normalize('NFKC', s.decode(sys.getfilesystemencoding()))
		    except:
		      try: s = unicodedata.normalize('NFKC', s.decode('ISO-8859-1'))
		      except:
		        try: s = unicodedata.normalize('NFKC', s)
		        except Exception, e:
		          Log(type(e).__name__ + ' exception precomposing: ' + str(e))
		# Strip control characters.
		s = re.sub(RE_UNICODE_CONTROL, '', s)
		return s
  



