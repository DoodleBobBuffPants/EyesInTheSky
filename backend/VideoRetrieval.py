# initiate drone video stream and media player
# must start execution from folder containing this file
import sys
from threading import Thread
# import pyparrot.Bebop  # library containing drone commands
import frontend.MediaPlayer as mp

sys.path.append("..")

print("Starting stream")  # starttest
# Bebop.start_video_stream()

# start video stream as separate process as it is blocking
vidPath = "../frontend/testvideo.mp4"  # should be rtp://localhost:55004 in reality
streamProc = Thread(target=mp.playVid, args=[vidPath])
streamProc.start()

# need to find a way to display video in a browser
# might be best to use this file as a starting point:
# - start video feed from drone
# - open player in separate thread
# - take frames and process them to get relative coordinates
# - give to movement module on request (will be concurrent so need threading)

print("Exiting stream")  # endtest
