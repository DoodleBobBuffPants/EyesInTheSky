#reads RTP packets
import socket
import bitstring

#function to uncover payload
def stripPacket(m):
	ba = bitstring.BitArray(bytes=m.encode('utf-8'))		#encode string and turn to bit array
	pt = ba[9:16]		#type of packet contents
	cc = ba[4:8]		#number of extra header fields
	print(pt.decode('utf-8'))		#for testing purposes
	return ba[(12+cc)*8:]		#bit contents

#create socket of required type, and bind to port
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)		#opens with ipv4 address and reads UDP packet
sock.bind(('', 55004))		#binds machine to port

#receive packet and get payload
#msg = sock.recv(4096)
#payload = stripPacket(msg)

'''
The received contents are H.264 encoded video. While we can put packets together, there doesn't seem to be documentation on
manual conversion to video or images, as all methods result in using opencv or other libraries/apps. Hence we adopt the 
opencv approach. This code can stay because it required far too much research to throw away.
'''

#test message
sock.close()
print("done")