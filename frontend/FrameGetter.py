# method for a separate thread to get frames concurrently to reduce lag
import cv2 as cv


def frame_getter(queue, vc):
    # continuously add frames to the shared thread-safe queue
    while True:
        success, frame = vc.read()
        if success:
            queue.put(frame)
            cv.waitKey(1)
