import math

from backend.movement import Drone
import time
from threading import Thread

# Create sample world that the Car and Drone move within

class Car:

    def __init__(self, start_x, start_y):
        self.x = start_x
        self.y = start_y

    # Can be any series of movements within the world. Should not be jumpy.
    def move(self, world_x_limit, world_y_limit):
        # Move in a circular motion
        # First move to the edge of circle from the start location
        while True:
            if self.x > 0.9 * world_x_limit and self.y > 0.5 * world_y_limit:
                break
            if self.x < 0.9 * world_x_limit:
                self.x += 0.1
            if self.y < 0.5 * world_y_limit:
                self.y += 0.1
            time.sleep(0.001)

        # Car should now be on the edge of the circle
        # Now continuously move around in the circle
        t = 0
        while True:
            self.x = world_x_limit / 2 + world_x_limit * 0.45 * math.cos(t)
            self.y = world_y_limit / 2 + world_y_limit * 0.45 * math.sin(t)
            t += 0.001
            time.sleep(0.01) # Not related to t value



class TestDrone(Drone):

    world_x = 0
    world_y = 0
    # The tilt angles won't directly convert into virtual world movement. Scale with this
    test_scale_factor = 0.1

    # Drone can see objects within a box.
    # Sqaure box, with side length given here - drone at the centre
    field_of_view = 25;

    def __init__(self, x, y):
        super(Drone, self).__init__()
        self.world_x = x
        self.world_y = y

    def print_coords(self):
        print(self.world_x, " ", self.world_y)

    def sleep(self, time_length):
        time.sleep(time_length)

    # Override the movement function so that movements are made within virtual world
    def move(self, vertical_movement):
        self.world_x += self.roll * self.movement_gap * self.test_scale_factor
        self.world_y += self.pitch * self.movement_gap * self.test_scale_factor

# Manages the coordinates of the drone and car in the virtual world
# Determines the virtual coordinates of the car in relation to the drone
class World():

    #car_x = 0
    #car_y = 0

    #drone_x = 0
    #drone_y = 0


    def __init__(self):

        self.drone_x = 0
        self.drone_y = 0

        self.car = Car(0,0)
        self.drone = TestDrone(self.drone_x, self.drone_y)

        # Define the size of the world
        self.world_size_x = 1000
        self.world_size_y = 1000

        # Choose a location for the car to start in the world
        #self.car_x = 0
        #self.car_y = 0

    # Calculates the position that the drone will see the car being in
    # Car must lie within the drones field of view, otherwise no location will be found
    def calculate_rel_position(self):
        x = float(self.car.x - self.drone_x) / self.drone.field_of_view
        y = float(self.car.y - self.drone_y) / self.drone.field_of_view
        if x < -1 or x > 1 or y < -1 or y > 1:
            self.drone.car_unknown = True
            return
        self.drone.car_x = x
        self.drone.car_y = y
        #print(x, y)

    # Manage the world in a thread - updating the location of the drone as it moves, and calculating relative position of the car
    def manage(self):
        while True:
            self.drone_x = self.drone.world_x
            self.drone_y = self.drone.world_y
            self.calculate_rel_position()


#car = Car(0, 0)
world = World()



# Start the world managing
thread1 = Thread(target = world.manage, args = [])
thread1.start()

# Set the drone to start following the car
thread2 = Thread(target = world.drone.follow_car, args = [])
thread2.start()

# Start the car moving
thread3 = Thread(target = world.car.move, args = [world.world_size_x, world.world_size_y])
thread3.start()

while True:
    #print(int(world.car_x), int(world.drone_x))
    #world.drone.print_coords()
    print(round(world.car.x, 2), " ", round(world.car.y, 2), "   ", round(world.drone_x, 2), " ", round(world.drone_y, 2))
    time.sleep(0.1)

#
"""
# Initialise objects
drone = TestDrone()
drone.print_coords()

thread = Thread(target = drone.follow_car, args = [])
thread.start()
print(True)
while True:
    drone.print_coords()
    time.sleep(0.1)
"""




#
