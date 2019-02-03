#read frames using opencv and display frames as a video
import cv2 as cv
from filelock import FileLock
def playVid(vidpath):
	vc = cv.VideoCapture(vidpath)
	#loop through each frame, making hand over for analysis easier
	while True:
		#successful read and frame
		success, frame = vc.read()
		if success:
			#display frame sequence
			cv.imshow('Video', frame)
			with FileLock("frame.jpg"):
				cv.imwrite("frame.jpg", frame)
			#close 'video' on key input 'q'
			if (cv.waitKey(7) == ord('q')):
				break
	#release resources
	vc.release()
	cv.destroyAllWindows()