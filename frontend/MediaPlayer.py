# read frames using opencv and display frames as a video
import cv2 as cv
from threading import Thread
# from queue import Queue
import backend.Lock as lock  # custom naive lock
import frontend.FrameGetter as fg
from frontend import Queue


def playVid(vidpath, bebop):
    # queue of frames
    queue = Queue.Queue()
    # new thread to get frames concurrently
    fgProc = Thread(target=fg.frameGetter, args=[queue, bebop, vidpath])
    fgProc.start()
    # loop through each frame, making hand over for analysis easier
    while True:
        # read frame
        frame = queue.get()
        cv.imshow('Video', frame)
        # synchronised write out of frame for concurrency control during analysis
        lock.take_lock()
        cv.imwrite("frame.jpg", frame)
        lock.release_lock()
        cv.waitKey(1)
    # release resources
    vc.release()
    cv.destroyAllWindows()
