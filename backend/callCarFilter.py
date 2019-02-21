# call CarFilterFrame.m using one frame at a time

# TODO: start from app? 

import matlab.engine
import cv2 as cv

def coords_from_centroid(centroids):
    # calculate values to send to movement from the centroids values
    # subtract by half of the image dimensions and then divide by half again before returning
    # gives them in range -1 and 1
    h = height/2.0
    w = width/2.0

    x = centroids[0]
    y = centroids[1]

    print("x ", x)
    x = (x - w)/w
    y = (h - y)/h
    print("x2 ", x)
    return x, y

# start the engine
eng = matlab.engine.start_matlab()

# get handle to matlab object CarFilter
cf = eng.CarFilterFrame() # number of args returned from matlab

# # VIDEO CAPTURE FOR TESTING FROM MP4
# vc = cv.VideoCapture('TrainingData/data3.mp4')
# ret, frame = vc.read()
# width, height = cv.GetSize(frame)


# load frame from top-level folder
frame = cv.imread("../frame.jpg")
height, width = frame.shape[:2]

# TODO: avoid copying a file so much and/or locking
# TODO: end at some point
while True:
    cv.imwrite("frame_for_filter.jpg", frame)
    # run the car filter with current frame
    a = eng.run(cf, "frame_for_filter.jpg")
    print("Centroids: ", a)

    if len(a) > 0:
        x, y = coords_from_centroid(a[0])

        print(x, y)
    
    frame = cv.imread("../frame.jpg")

    # ret, frame = vc.read()

