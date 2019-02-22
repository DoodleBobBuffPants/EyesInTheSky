import backend.server.app as App
from pyparrot.DroneVisionGUI import DroneVisionGUI
from threading import Thread
import platform
import cv2
import frontend.Lock as Lock

drone = App.drone


class UserVision:
    def __init__(self, vision):
        self.vision = vision
        self.lock = Lock.Lock()

    def save_pictures(self, args):
        img = self.vision.get_latest_valid_picture()

        if (img is not None):
            self.lock.take_lock()
            cv2.imwrite("frame.jpg", img)
            self.lock.release_lock()

# Launch the web server in separate thread.
appThread = Thread(target=App.app.run, args = [])
appThread.start()

if platform.system() != "Windows":
    bebopVision = DroneVisionGUI(drone, is_bebop=True, user_code_to_run=None, user_args=(drone,))
    userVision = UserVision(bebopVision)
    bebopVision.set_user_callback_function(userVision.save_pictures, user_callback_args=None)
    bebopVision.open_video()


