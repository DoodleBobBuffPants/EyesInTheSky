#initiate drone video stream and media player
#must start execution from folder containing this file
import sys
sys.path.append("..")
from threading import Thread
from pyparrot.Bebop import Bebop		#library containing drone commands
import frontend.MediaPlayer as mp

print("Starting stream") 	#starttest

bebop = Bebop()
bebop.connect(10)
bebop.set_video_resolutions("rec1080_stream480")
bebop.set_video_framerate("24_FPS")
#bebop.set_video_stream_mode(mode="high_reliability_low_framerate")

#start video stream as separate process as it is blocking
vidPath = "../frontend/bebop.sdp"		#"../frontend/testvideo.mp4"
streamProc = Thread(target = mp.playVid, args = [vidPath])
streamProc.start()

bebop.start_video_stream()

#need to find a way to display video in a browser
#might be best to use this file as a starting point:
# - start video feed from drone
# - open player in separate thread
# - take frames and process them to get relative coordinates
# - give to movement module on request (will be concurrent so need threading)

print("Exiting stream")		#endtest