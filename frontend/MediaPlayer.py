#read frames using opencv and display frames as a video
import cv2 as cv
def playVid(vidpath):
	vc = cv.VideoCapture(vidpath)
	#loop through each frame, making hand over for analysis easier
	while(vc.isOpened()):
		#successful read and frame
		success, frame = vc.read()
		if success:
			#display frame sequence
	  		cv.imshow('Video', frame)
	  		cv.imwrite("frame.jpg", frame)
	  		#close 'video' on key input 'q'
	  		if (cv.waitKey(25) & 0xFF) == ord('q'):
	  			break
		else:
			break
	#release resources
	vc.release()
	cv.destroyAllWindows()
vid = "testvideo.mp4"		#test video - should use rtp://localhost:8080
playVid(vid)