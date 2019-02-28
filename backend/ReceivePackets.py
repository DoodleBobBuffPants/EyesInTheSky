# reads RTP packets
import socket
import bitstring

# import drone
from pyparrot.Bebop import Bebop


# function to uncover payload
def stripPacket(m):
    ba = bitstring.BitArray(bytes=m)  # encode string and turn to bit array
    pt = ba[9:16]  # type of packet contents
    cc = ba[4:8]  # number of extra header fields
    print(pt.uint)  # for testing purposes
    # return ba[(12 + cc) * 8:]  # bit contents

# create drone and start video
drone = Bebop()
drone.connect(10)
drone.set_video_resolutions("rec1080_stream480")
drone.set_video_framerate("24_FPS")
drone.start_video_stream()

# create socket of required type, and bind to port
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # opens with ipv4 address and reads UDP packet
sock.bind(('192.168.42.63', 55004))  # binds machine to port

# receive packet and get payload
for _ in range(10):
    msg = sock.recv(4096)
    stripPacket(msg)
    # payload = stripPacket(msg)

'''
The received contents are H.264 encoded video. While we can put packets together, there doesn't seem to be documentation on
manual conversion to video or images, as all methods result in using opencv or other libraries/apps. Hence we adopt the 
opencv approach. This code can stay because it required far too much research to throw away.
'''

# test message
sock.close()
drone.disconnect()
print("done")
