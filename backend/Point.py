# for shared coordinates
# lock for synchronized use
import frontend.Lock as Lock

class Point:
    # set up
    def __init__(self):
        self.x = 0
        self.y = 0
        self.lock = Lock.Lock()

    def set(self, nx, ny):
        self.lock.take_lock()
        self.x = nx
        self.y = ny
        self.lock.release_lock()

    def get(self):
        self.lock.take_lock()
        rx = self.x
        ry = self.y
        self.lock.release_lock()
        return rx, ry