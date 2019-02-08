from pyparrot.Bebop import Bebop
import math
import time


class DroneException(Exception):
    pass


# TODO: subclass from pyparrot.bebop
class Drone:
    drone = None

    # Stores the position of the car in relation to the drone.
    # Each value in range -1 to 1
    car_rel_x = 0
    car_rel_y = 0

    # Safety flags
    car_unknown = False  # car out of frame
    stop_flight = False  # emergency stop

    # Use this value to adjust drones movement - not sure whether strictly required yet
    # Max tilt angles also used for this
    scale_factor = 0.1

    # Time in seconds between instructions being sent to the drone. An arbitrary choice
    movement_gap = 0.01

    # Current values of angles, from -100 to 100 (essentially a % of the set max value)
    roll = 0
    pitch = 0
    yaw = 0

    def __init__(self, max_tilt=5):
        # Set limits on drone performance
        # e.g. max tilt angle

        # Should scaling mechanism be proportional to height of drone?

        # Add safety mechanism to allow immediate landing of the drone

        self.drone = Bebop()
        # connection and takeoff should be launched from here
        self.drone.set_max_tilt(max_tilt)

        self.connected = self.drone.connect(10)
        # raise DroneException - dont raise so we can actually test without the whole thing dying

        self.drone.set_max_tilt(max_tilt)
        # Must make sure the camera is always pointing down - even when the drone is at an angle

    def takeoff(self):
        if self.connected:
            self.drone.safe_takeoff(10)
        else:
            raise DroneException("Not connected")

    # One option for updating the coordinates of the car's relative position.
    # Can be called by the image recognition area.
    # Alternatively can retrieve most up to date version of coordinates from the image recognition file.
    def update_coords(self, new_x, new_y):
        self.car_rel_x = new_x
        self.car_rel_y = new_y

    # For emergency manual override
    def immediate_land(self):
        # Go to level flight
        self.roll = 0
        self.pitch = 0
        self.yaw = 0

        # Perform a safe land
        self.stop_flight = True

        self.pitch = 0
        self.roll = 0
        self.yaw = 0
        self.drone.safe_land(5)

    def teardown(self):
        self.drone.disconnect()

    # Given one of the coordinates, return the speed required to move in that direction.
    # Returned value is percentage of maximum tilt angle (-100 to 100). May be scaled elsewhere
    @staticmethod
    def calculate_speed(coord):
        # Using equation:
        #   y = 100 * sqrt(1 - (x-1)^2) for 0 < x < 1
        # For values -1 < 1, this formula in used
        #   y = x/|x| * sqrt(1 - (|x|-1)^2) for -1 < x < 1

        # Alternative functions available:
        #   y = 100 * sin(pi/2 * x)

        speed = 100 * math.sqrt(1 - (abs(coord) - 1) ** 2)
        if coord < 0:
            return speed * -1
        else:
            return speed

    def sleep(self, time_length):
        self.drone.smart_sleep(time_length)

    def move(self, vertical_movement):
        print(self.roll, self.pitch, self.yaw)
        if int(self.roll) == 0 and int(self.pitch) == 0 and int(self.yaw) == 0:
            self.drone.flat_trim(0)
        else:
            self.drone.fly_direct(int(self.roll), int(self.pitch), int(self.yaw),
                                  vertical_movement=int(vertical_movement),
                                  duration=self.movement_gap)

    def hover(self):
        self.pitch = 0
        self.roll = 0
        self.yaw = 0

    def slowdown(self, x, duration):
        print([i * 0.01 for i in range(int(10000 * x), -int(10000 * x) - 1, -int(100 * x))])
        for i in [i * 0.01 for i in range(int(10000 * x), -int(10000 * x) - 1, - int(100 * x))]:
            print("i: ", i)
            self.car_rel_x = i
            self.car_rel_y = i
            time.sleep(duration / 100)

        self.car_rel_x = 0
        self.car_rel_y = 0

    # Runs in a continuous loop that sets the drone movements based on the cars location.
    # Should be run in a separate thread.
    # Uses the fly_direct(roll, pitch, yaw, vertical_movement, duration) command
    # Initially don't use yaw. Use forward-backward and side-to-side movements.
    # Alternative : Change so that spins to face the car and then always moves forwards
    def follow_car(self):
        while True:
            if self.stop_flight:
                # self.immediate_land()
                break
            if self.car_unknown:
                self.lost_car()
                continue
            # Care using time.sleep or drone.safe_sleep()
            # Check pyparrot documentation for this

            # v. naive
            # could be replaced by more sophisticated algorithm e.g. PID
            self.roll = self.calculate_speed(self.car_rel_x) * self.scale_factor
            self.pitch = self.calculate_speed(self.car_rel_y) * self.scale_factor
            # print(" -  - ", self.calculate_speed(self.car_x))

            self.move(0)

            # TODO: Could use move_relative here using drone's GPS ???

            # Care using time.sleep or drone.safe_sleep()
            # Check pyparrot documentation for this
            self.sleep(self.movement_gap)

    # In the event that the car cannot be found in the image
    # this method can be called and the drone can try and find the car.
    # Options:  fly upwards to increase field of view.
    #           Raise the angle of the camera slightly and spin around to find it
    #               Then gradually return the camera to its original vertically down angle.
    def lost_car(self):
        # First step: become stationary
        self.roll = 0
        self.pitch = 0
        self.yaw = 0
