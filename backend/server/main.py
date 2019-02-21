import backend.server.app as App
from pyparrot.DroneVisionGUI import DroneVisionGUI
from threading import Thread
import platform

drone = App.drone


class UserVision:
    def __init__(self, vision):
        self.index = 0
        self.vision = vision

    def save_pictures(self, args):
        #print("saving picture")
        img = self.vision.get_latest_valid_picture()

        if (img is not None):
            filename = "test_image_%06d.png" % self.index
            #cv2.imwrite(filename, img)
            self.index +=1


# Launch the web server in seperate thread.
appThread = Thread(target=App.app.run, args = [])
appThread.start()

if platform.system() != "Windows":
    bebopVision = DroneVisionGUI(drone, is_bebop=True, user_code_to_run=None, user_args=(drone,))
    userVision = UserVision(bebopVision)
    bebopVision.set_user_callback_function(userVision.save_pictures, user_callback_args=None)
    bebopVision.open_video()


