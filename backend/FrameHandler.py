import cv2 as cv
import backend.Lock as Lock 	# custom naive lock

class FrameHandler:

	# set up lock for synchronised access
	def __init__(self):
		self.lock = Lock.Lock()

	# save numpy array 'frame'
	def writeFrame(self, npframe):
		self.frame = npframe
		self.take_lock()
		cv.imwrite("frame.jpg", self.frame)
		self.release_lock()

	def getFrame(self):
		return self.frame

	# wrap the lock to make it accessible in a cleaner way
	def take_lock(self):
		self.lock.take_lock()
	def release_lock(self):
		self.lock.release_lock()