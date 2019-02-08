"""naive lock, but works for our use"""
# lock variable
lock = 0


# take lock
def take_lock():
    # spin while taken
    try:
        while lock == 1:
            pass
        lock = 1
    except NameError:
        lock = 1


# release lock
def release_lock():
    lock = 0
