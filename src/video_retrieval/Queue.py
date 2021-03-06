# custom thread-safe queue class
import src.video_retrieval.Lock as Lock  # lock to handle synchronisation


class Queue:

    # initialise buffer
    def __init__(self, size=200):
        self.buf = []
        self.lock = Lock.Lock()
        self.maxsize = size
        self.first = True

    # return an item if there is one
    def get(self):
        while len(self.buf) == 0:
            pass
        self.lock.take_lock()
        if not self.first:
            ret = self.buf[0]
            self.buf = self.buf[1:]
        else:
            ret = self.buf[-1]
            self.buf = []
            self.first = False
        self.lock.release_lock()
        return ret

    # put an item at the end of the list
    def put(self, item):
        while len(self.buf) > self.maxsize:
            pass
        self.lock.take_lock()
        self.buf = self.buf + [item]
        self.lock.release_lock()
