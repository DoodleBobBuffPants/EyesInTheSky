"""naive lock, but works for our use"""


class Lock:

    def __init__(self):
        self.lock = 0

    # take lock
    def take_lock(self):
        # spin while taken
        while self.lock == 1:
            pass
        self.lock = 1

    # release lock
    def release_lock(self):
        self.lock = 0
