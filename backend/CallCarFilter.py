# call CarFilterFrame.m using one frame at a time

# TODO: test from app again
# TODO: start matlab engine earlier
from threading import Thread

import matlab.engine
import cv2 as cv
import os

from PIL import Image

from backend import FindRed
from frontend import Queue
import frontend.FrameGetter as fg


def call_car_filter(bebop, lock, source='drone'):
    # start the engine and cd to the matlab code
    # eng = matlab.engine.start_matlab()
    # eng.cd("./backend/Matlab")
    # get handle to matlab object CarFilter
    # cf = eng.CarFilterFrame() # number of args returned from matlab (default 1)

    frame = None
    # load frame from source (either video or drone)

    # new thread to get frames concurrently
    bebop.start_video_stream()
    vc = cv.VideoCapture("frontend/bebop.sdp")

    # frame, vc = load_frame(bebop, lock, source)

    success = False
    while not success:
        success, frame = vc.read()

    height, width = frame.shape[:2]

    while True:
        a = FindRed.find_red(frame)
        # if the filter returns any centroids update bebop
        if len(a) > 0:
            x, y = coords_from_centroid(a, width, height)
            print(x, y)
            bebop.update_coords(x, y)


def coords_from_centroid(centroids, width, height):
    # calculate values to send to movement from the centroids values
    # subtract by half of the image dimensions and then divide by half again before returning
    # gives them in range -1 and 1
    h = height / 2.0
    w = width / 2.0

    x = centroids[0]
    y = centroids[1]

    x = (x - w) / w
    y = (h - y) / h
    return x, y
