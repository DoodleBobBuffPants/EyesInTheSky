# test for custom thread-safe queue
import src.video_retrieval.Queue as Queue  # custom queue
from threading import Thread  # prod/cons threads

# initialise queue and counter
queue = Queue.Queue()


# consumer method
def consumer(q):
    for _ in range(10):
        print(q.get())


# producer method
def producer(q):
    for _ in range(10):
        q.put(1)


# create threads
cons = Thread(target=consumer, args=[queue])
prod = Thread(target=producer, args=[queue])
prod.start()
cons.start()

# wait for termination
prod.join()
cons.join()
