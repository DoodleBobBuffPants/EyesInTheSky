import cv2


class DroneCamera(object):

    def __init__(self, drone):
        drone.set_video_resolutions("rec1080_stream480")
        drone.set_video_framerate("24_FPS")
        drone.set_video_stream_mode('low_latency')
        drone.start_video_stream()
        # start video stream as separate process as it is blocking
        vid_path = "video_retrieval/bebop.sdp"

        self.vc = cv2.VideoCapture(vid_path)
        self.vc.set(cv2.CAP_PROP_FPS, 24)

    def get_frame(self):
        success = False
        frame = None
        while not success:
            success, frame = self.vc.read()
        return frame
