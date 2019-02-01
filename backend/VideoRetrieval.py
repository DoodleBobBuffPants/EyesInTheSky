#Receive video from drone and pass on to movement modules
import pyparrot.Bebop

print("Starting stream") 	#starttest
#Bebop.start_video_stream()

#drone sends rtp packets
#need to find a way to save them
#and process them into video

#alternatively VLC player will automatically play the video


#Need to start VLC player from python with an SDP file that handles reading packets from the drone
#Then open a browser at localhost:8080 to display video stream there

#Might be best to use this file as a starting point:
# - start video feed from drone
# - open player
# - take frames and process them to get relative coordinates
# - give to movement module on request (will be concurrent so need threadings)

print("Exiting stream")		#endtest