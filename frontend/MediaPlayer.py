# read frames using opencv and display frames as a video
import cv2 as cv
from threading import Thread
import frontend.Lock as Lock
import frontend.FrameGetter as fg
from frontend import Queue

class MediaPlayer:

    # initialise state
    def __init__(self):
        self.lock = Lock.Lock()

    # get lock reference
    def getLock():
        return self.lock

    def playVid(self, vidpath, bebop):
        # queue of frames
        queue = Queue.Queue()
        # new thread to get frames concurrently
        bebop.start_video_stream()
        fgProc = Thread(target=fg.frameGetter, args=[queue, bebop, vidpath])
        fgProc.daemon = True
        fgProc.start()
        # loop through each frame, making hand over for analysis easier
        while True:
            # read frame
            frame = queue.get()
            cv.imshow('Video', frame)
            # synchronised write out of frame for concurrency control during analysis
            self.lock.take_lock()
            cv.imwrite("frame.jpg", frame)
            self.lock.release_lock()
            if cv.waitKey(2) == ord('q'):
            	# release resources
            	cv.destroyAllWindows()
                bebop.stop_video_stream()
            	break