# method for a separate thread to get frames concurrently to reduce lag
import cv2 as cv
def frameGetter(queue, bebop, vidpath):
	# start stream and capturer here to reduce latency
	bebop.start_video_stream()
	vc = cv.VideoCapture(vidpath)
	# continuously add frames to the shared thread-safe queue
	while True:
		success, frame = vc.read()
		if success:
			queue.put(frame)
			cv.waitKey(1)