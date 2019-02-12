# custom thread-safe queue class
import frontend.Lock as lock  # lock to handle synchronisation


class Queue:

    # initialise buffer
    def __init__(self):
        self.buf = []

    # return an item if there is one
    def get(self):
        while len(self.buf) == 0:
            pass
        lock.take_lock()
        ret = self.buf[0]
        self.buf = self.buf[1:]
        lock.release_lock()
        return ret

    # put an item at the end of the list
    def put(self, item):
        lock.take_lock()
        self.buf = self.buf + [item]
        lock.release_lock()
