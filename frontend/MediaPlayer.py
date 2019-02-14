# read frames using opencv and display frames as a video
import cv2 as cv
from threading import Thread
import backend.FrameHandler as FH
import frontend.FrameGetter as fg
from frontend import Queue


def playVid(vidpath, bebop):
    # queue of frames
    queue = Queue.Queue()
    fh = FH.FrameHandler()
    # new thread to get frames concurrently
    fgProc = Thread(target=fg.frameGetter, args=[queue, bebop, vidpath])
    fgProc.daemon = True
    fgProc.start()
    # loop through each frame, making hand over for analysis easier
    while True:
        # read frame
        frame = queue.get()
        cv.imshow('Video', frame)
        # synchronised write out of frame for concurrency control during analysis
        fh.writeFrame(frame)
        if cv.waitKey(1) == ord('q'):
        	# release resources
        	cv.destroyAllWindows()
        	break