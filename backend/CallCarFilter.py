# call CarFilterFrame.m using one frame at a time

# TODO: test from app again
# TODO: start matlab engine earlier
from threading import Thread

import matlab.engine
import cv2 as cv
import os

from PIL import Image
from pyparrot.DroneVisionGUI import DroneVisionGUI

from backend import FindRed
from frontend import Queue
import frontend.FrameGetter as fg


class UserVision:
    def __init__(self, vision):
        self.vision = vision
        #self.lock = App.mp.getLock()

    def save_pictures(self, args):
        img = self.vision.get_latest_valid_picture()

        if (img is not None):
            self.lock.take_lock()
            #cv2.imwrite("frame.jpg", img)
            self.lock.release_lock()

    # Returns a numpy array with the latest image
    def get_latest_image(self):
        img = self.vision.get_latest_valid_picture()
        return img

def call_car_filter(bebop, lock, source='drone'):
    # start the engine and cd to the matlab code
    #eng = matlab.engine.start_matlab()
    #eng.cd("./backend/Matlab")
    # get handle to matlab object CarFilter
    #cf = eng.CarFilterFrame() # number of args returned from matlab (default 1)

    frame = None
    # load frame from source (either video or drone)

    """queue = Queue.Queue()
    # new thread to get frames concurrently
    bebop.start_video_stream()
    vc = cv.VideoCapture("frontend/bebop.sdp")
    fgProc = Thread(target=fg.frameGetter, args=[queue, vc])
    fgProc.daemon = True
    fgProc.start()"""

    bebopVision = DroneVisionGUI(bebop, is_bebop=True, user_code_to_run=None, user_args=(bebop,))
    userVision = UserVision(bebopVision)
    bebopVision.set_user_callback_function(userVision.save_pictures, user_callback_args=None)
    bebopVision.open_video()

    #frame, vc = load_frame(bebop, lock, source)
    frame = bebopVision.get_latest_valid_picture()

    height, width = frame.shape[:2] 

    # TODO: avoid copying a file so much and/or locking?
    # TODO: end at some point
    # TODO: neater end for end of a video file
    while True:
        # write the frame for the filter to read from
        # cv.imwrite("backend/frame_for_filter.jpg", frame)
        # run the car filter with current frame
        #a = eng.run(cf, "../frame_for_filter.jpg")
        a = FindRed.find_red(frame)
        #print(a)

        # if the filter returns any centroids update bebop
        if len(a) > 0:
            x, y = coords_from_centroid(a, width, height)
            print(x, y)
            bebop.update_coords(x, y)
        #frame, vc = load_frame(bebop, lock, source, vc)
        #print(frame)
        im = Image.fromarray(frame.astype('uint8'))
        #im.show()
        frame = queue.get()


def load_frame(bebop, lock, source, vc=None):

    # load a frame from either the drone or an mp4
    if source == 'drone':
        lock.take_lock()
        frame = None
        while frame is None:
            frame = cv.imread("frame.jpg")
        lock.release_lock()
        return frame, vc
    elif source == 'mp4':
        if vc is None: # set up video capture 
            vc = cv.VideoCapture('backend/TrainingData/data3.mp4')
        ret, frame = vc.read()
        return frame, vc
    else:
        raise ValueError("No valid frame source given: must be mp4 or drone.")

def coords_from_centroid(centroids, width, height):
    # calculate values to send to movement from the centroids values
    # subtract by half of the image dimensions and then divide by half again before returning
    # gives them in range -1 and 1
    h = height/2.0
    w = width/2.0

    x = centroids[0]
    y = centroids[1]

    x = (x - w)/w
    y = (h - y)/h
    return x, y

# to test directly calling this file
# optional argument: '-mp4': uses training data 3
if __name__ == '__main__':
    import sys
    from frontend import Lock   

    if len(sys.argv) > 1:
        if sys.argv[1] == "-mp4":
            lock = Lock.Lock()
            call_car_filter(1, lock, 'mp4')
    else:
        lock = Lock.Lock()
        call_car_filter(1, lock)

