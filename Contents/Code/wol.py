######################################################################################################################
#	WOL module unit					
#
#	Author: dane22, a Plex Community member
#
# NAME variable must be defined in the calling unit, and is the name of the application
#
# This module is the main module for WakOnLan, a WebTools Module
#
######################################################################################################################

import socket
import struct

class wol(object):
	# Defaults used by the rest of the class
	def __init__(self):
		
		return

	''' Grap the tornado req, and process it '''
	def reqprocessPost(self, req):		
		function = req.get_argument('function', 'missing')
		if function == 'missing':
			req.clear()
			req.set_status(412)
			req.finish('Missing function parameter')
		elif function == 'wol':
			return self.wol(req)
		else:
			req.clear()
			req.set_status(412)
			req.finish('Unknown function call')

	''' This metode will wake up a mashine. '''
	def wol(self, req):
		Log.Debug('Starting wol.wol function')
		try:
			macaddress = req.get_argument('mac', 'missing')
			if macaddress == 'missing':
				req.clear()
				req.set_status(412)
				req.finish('Missing Mac Address')
				return req
			

			# Check macaddress format and try to compensate.
			if len(macaddress) == 12:
				pass
			elif len(macaddress) == 12 + 5:
				sep = macaddress[2]
				macaddress = macaddress.replace(sep, '')
			else:
				print 'Ged', 'Incorrect MAC address format', macaddress
				raise ValueError('Incorrect MAC address format')
 
			# Pad the synchronization stream.
			data = ''.join(['FFFFFFFFFFFF', macaddress * 20])
			send_data = '' 

			# Split up the hex values and pack.
			for i in range(0, len(data), 2):
				send_data = ''.join([send_data, struct.pack('B', int(data[i: i + 2], 16))])

			# Broadcast it to the LAN.
			sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
			sock.sendto(send_data, ('<broadcast>', 7))

			req.clear()
			req.set_status(200)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish('Magic WOL packet dispatched')
		except Exception, e:
			Log.Debug('Fatal error happened in wol.wol: ' + str(e))
			req.clear()
			req.set_status(500)
			req.set_header('Content-Type', 'application/json; charset=utf-8')
			req.finish('Fatal error happened in wol.wol: ' + str(e))


