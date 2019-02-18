# save frames asynchronously
import cv2 as cv
import frontend.Lock as Lock

def frameSaver(queue, lock):
    while True:
        lock.take_lock()
        cv.imwrite("frame.jpg", queue.peek())   # peek non existant
        lock.release_lock()