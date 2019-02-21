# read frames using opencv and display frames as a video
import cv2 as cv
from threading import Thread
import frontend.Lock as Lock
import frontend.FrameGetter as fg
import frontend.FrameSaver as fs
from frontend import Queue
import backend.CallCarFilter as cf

class MediaPlayer:

    # initialise state
    def __init__(self):
        self.lock = Lock.Lock()

    # get lock reference
    def getLock(self):
        return self.lock

    def playVid(self, vidpath, bebop):
        # queue of frames
        queue = Queue.Queue()
        # new thread to get frames concurrently
        bebop.start_video_stream()
        vc = cv.VideoCapture(vidpath)
        fgProc = Thread(target=fg.frameGetter, args=[queue, vc])
        fgProc.daemon = True
        fgProc.start()
        
        # loop through each frame, making hand over for analysis easier
        while True:
            # read frame
            frame = queue.get()
            # synchronised write out of frame for concurrency control during analysis
            self.lock.take_lock()
            cv.imwrite("frame.jpg", frame)
            self.lock.release_lock()
            cv.imshow('Video', frame)
            if cv.waitKey(1) == ord('q'):
            	# exit
                break
        # relese resources
        cv.destroyAllWindows()
        vc.release()
        bebop.stop_video_stream()
