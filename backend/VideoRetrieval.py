#Initiate drone video stream and media player
import pyparrot.Bebop		#library containing drone commands

print("Starting stream") 	#starttest
#Bebop.start_video_stream()

#drone sends rtp packets
#need to find a way to save them
#and process them into video

#can use opencv to process video by fram
#need to find a way to display video in a browser

#might be best to use this file as a starting point:
# - start video feed from drone
# - open player
# - take frames and process them to get relative coordinates
# - give to movement module on request (will be concurrent so need threadings)

print("Exiting stream")		#endtest