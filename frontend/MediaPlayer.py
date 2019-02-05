# read frames using opencv and display frames as a video
import sys
sys.path.append("..")
import cv2 as cv
# from filelock import FileLock
import backend.Lock as lock 		# custom naive lock
def playVid(vidpath, bebop):
	# start stream here to reduce latency
	bebop.start_video_stream()
	vc = cv.VideoCapture(vidpath)
	# loop through each frame, making hand over for analysis easier
	while True:
		# successful read and frame
		success, frame = vc.read()
		if success:
			# display frame sequence
			cv.imshow('Video', frame)
			# synchronised write out of frame for concurrency control during analysis
			lock.take_lock()
			cv.imwrite("frame.jpg", frame)
			lock.release_lock()
			cv.waitKey(1)
	# release resources
	vc.release()
	cv.destroyAllWindows()