# call CarFilterFrame.m using one frame at a time

# % TODO: calculate values to send to movement from the centroids values
# %       subtract by half of the image dimensions and then divide by half again before returning
# %       gives them in range -1 and 1

# TODO: link to video feed from drone

# TODO: start from app? 

# TODO:
import matlab.engine
import cv2 as cv

# start the engine
eng = matlab.engine.start_matlab()

# get handle to matlab object CarFilter
cf = eng.CarFilterFrame() # number of args returned from matlab

# video capture for testing from mp4
vc = cv.VideoCapture('TrainingData/data3.mp4')

ret, frame = vc.read()

while(ret):
    cv.imwrite("frame_for_filter.jpg", frame)
    # run the car filter with current frame
    a = eng.run(cf, "frame_for_filter.jpg")
    print("Centroids: ", a)
    
    ret, frame = vc.read()
