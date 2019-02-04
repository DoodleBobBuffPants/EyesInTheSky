from pyparrot.Bebop import Bebop
import math

class Drone:

    drone = None

    # Stores the position of the car in relation to the drone.
    # Each value in range -1 to 1
    car_x = 0
    car_y = 0

    # Use this flag if the car can't be found in the video feed
    car_unknown = False

    # Use this value to adjust drones movement - not sure whether strictly required yet
    # Max tilt angles also used for this
    scale_factor = 1

    # Time in seconds between instructions being sent to the drone. An arbitrary choice
    movement_gap = 0.1

    # A flag that when set will stop the drone following the car
    # Safety mechanism
    stop_flight = False

    def __init__(self):
        # Set limits on drone performance
        # e.g. max tilt angle

        # Should scaling mechanism be proportional to height of drone?

        # Add safety mechanism to allow immediate landing of the drone

        self.drone = Bebop()
        # connection and takeoff should be launched from here

        # Must make sure the camera is always pointing down - even when the drone is at an angle

    # One option for updating the coordinates of the car's relative position.
    # Can be called by the image recognition area.
    # Alternatively can retrieve most up to date version of coordinates from the image recognition file.
    def update_coords(self, new_x, new_y):
        pass

    # For emergency manual override
    def immediate_land(self):
        # Set the stop_flight flag
        # Go to level flight
        # Perform safe land
        pass

    # Given one of the coordinates, return the speed required to move in that direction.
    # Returned value is percentage of maximum tilt angle (-100 to 100). May be scaled elsewhere
    def calculate_speed(self, coord):
        # Using equation:
        #   y = 100 * sqrt(1 - (x-1)^2) for 0 < x < 1
        # For values -1 < 1, this formula in used
        #   y = x/|x| * sqrt(1 - (|x|-1)^2) for -1 < x < 1

        # Alternative functions available:
        #   y = 100 * sin(pi/2 * x)

        speed = 100 * math.sqrt(1 - (abs(coord) - 1)**2)
        if coord < 0:
            return speed * -1
        else:
            return speed

    def sleep(self, time_length):
        self.drone.safe_sleep(time_length)

    def set_movement(self, roll, pitch, yaw, vertical_movement, duration):
        self.drone.fly_direct(roll=roll, pitch=pitch, yaw=yaw, vertical_movement=vertical_movement, duration=duration)

    # Runs in a continuous loop that sets the drone movements based on the cars location.
    # Should be run in a separate thread.
    # Uses the fly_direct(roll, pitch, yaw, vertical_movement, duration) command
    # Initially don't use yaw. Use forward-backward and side-to-side movements.
    # Alternative : Change so that spins to face the car and then always moves forwards
    def follow_car(self):
        while True:
            if self.stop_flight:
                self.immediate_land()
                break
            if self.car_unknown:
                self.lost_car()
            # Care using time.sleep or drone.safe_sleep()
            # Check pyparrot documentation for this
            speed_x = self.calculate_speed(self.car_x) * self.scale_factor
            speed_y = self.calculate_speed(self.car_y) * self.scale_factor
            self.set_movement(speed_x, speed_y, 0, 0, self.movement_gap)

            # Care using time.sleep or drone.safe_sleep()
            # Check pyparrot documentation for this
            self.sleep(self.movement_gap)  # deliberately non-existent function for now


    # In the event that the car cannot be found in the image
    # this method can be called and the drone can try and find the car.
    # Options:  fly upwards to increase field of view.
    #           Raise the angle of the camera slightly and spin around to find it
    #               Then gradually return the camera to its original vertically down angle.
    def lost_car(self):
        pass







#