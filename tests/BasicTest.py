import src.movement as movement
import time
from threading import Thread

drone = movement.FollowingDrone()  # creates connection, and takes off

drone.car_rel_y = 0.1
drone.car_rel_x = 0.1

thread = Thread(target=drone.follow_car, args=[])
thread.start()

time.sleep(3)

drone.car_rel_y = 0
drone.safe_land(3)
drone.emergency_land()
drone.disconnect()
