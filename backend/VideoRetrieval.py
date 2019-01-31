#Receive video from drone and pass on to movement modules
import pyparrot.Bebop

print("Starting stream") 	#starttest
#Bebop.start_video_stream()

#drone sends rtp packets
#need to find a way to save them
#and process them into video

#alternatively VLC player will automatically play the video

print("Exiting stream")		#endtest