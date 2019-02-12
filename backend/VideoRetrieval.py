# initiate drone video stream and media player
# must start execution from folder containing this file
import sys

sys.path.append("..")
from threading import Thread
from pyparrot.Bebop import Bebop  # library containing drone commands
import frontend.MediaPlayer as mp

bebop = Bebop()
bebop.connect(10)
# bebop.set_video_resolutions("rec1080_stream480")
# bebop.set_video_framerate("24_FPS")

# start video stream as separate process as it is blocking
vidPath = "../frontend/bebop.sdp"
streamProc = Thread(target=mp.playVid, args=[vidPath, bebop])
streamProc.start()
