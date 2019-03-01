# save frames asynchronously
import cv2 as cv


def frame_saver(queue, lock):
    while True:
        lock.take_lock()
        cv.imwrite("frame.jpg", queue.peek())  # peek non existent
        lock.release_lock()
