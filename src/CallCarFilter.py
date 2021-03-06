# call CarFilterFrame.m using one frame at a time

import matlab.engine
import cv2 as cv

# noinspection PyUnresolvedReferences
def call_car_filter(bebop, lock, source='drone'):
    engines = matlab.engine.find_matlab()

    if len(engines) > 0:
        print("Connecting to matlab engine...")
        eng = matlab.engine.connect_matlab()
    else:
        # start the engine and cd to the matlab code
        print("Starting matlab...")
        eng = matlab.engine.start_matlab()

    # cd to the matlab code in engine 
    eng.cd("./src/matlab")
    # get handle to matlab object CarFilter
    cf = eng.CarFilterFrame()  # number of args returned from matlab (default 1)
    print("Matlab engine ready.")

    # load frame from source (either video or drone)
    frame, vc = load_frame(lock, source)

    height, width = frame.shape[:2]

    while True:
        # write the frame for the filter to read from
        cv.imwrite("src/matlab/frame_for_filter.jpg", frame)
        # run the car filter with current frame
        a = eng.run(cf, "frame_for_filter.jpg")

        # if the filter returns any centroids update bebop
        if len(a) > 0:
            x, y = coords_from_centroid(a[0], width, height)
            if source == 'drone':
                bebop.update_coords(x, y)
            else:
                print(x, y)
        frame, vc = load_frame(lock, source, vc)


def load_frame(lock, source, vc=None):
    # load a frame from either the drone or an mp4
    if source == 'drone':
        lock.take_lock()
        frame = None
        while frame is None:
            frame = cv.imread("frame.jpg")
        lock.release_lock()
        return frame, vc
    elif source == 'mp4':
        if vc is None:  # set up video capture
            vc = cv.VideoCapture('src/matlab/training_data/droneData2.mp4')
        ret, frame = vc.read()
        return frame, vc
    else:
        raise ValueError("No valid frame source given: must be mp4 or drone.")


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


# to test directly calling this file
# optional argument: '-mp4': uses droneData2.mp4
if __name__ == '__main__':
    import sys
    from src.video_retrieval import Lock

    if len(sys.argv) > 1:
        if sys.argv[1] == "-mp4":
            test_lock = Lock.Lock()
            call_car_filter(1, test_lock, 'mp4')
    else:
        test_lock = Lock.Lock()
        call_car_filter(1, test_lock)
