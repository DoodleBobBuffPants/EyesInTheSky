from pyparrot.Bebop import Bebop
import backend.Point as Point
import math
import time


class DroneException(Exception):
    pass


class DroneNotConnectedException(DroneException):
    pass


class FollowingDrone(Bebop):
    # Use this value to adjust drones movement - not sure whether strictly required yet
    # Max tilt angles also used for this
    scale_factor = 0.1

    # Time in seconds between instructions being sent to the drone. An arbitrary choice
    # TODO - this should probably be the same rate that new car coordinates are received
    movement_gap: float = 0.1

    # Estimated time that the video feed is delayed by
    video_delay = 0.5

    # Position of the car in relation to the drone.
    # Each value in range -1 to 1
    # User properties here to avoid setting to values outside [-1,1]
    _car_rel_y: float = 0
    _car_rel_x: float = 0

    prev_car_rel_x: float = 0
    prev_car_rel_y: float = 0

    finding_car: bool = False

    battery = 100

    @property
    def car_rel_x(self):
        return self._car_rel_x

    @car_rel_x.setter
    def car_rel_x(self, x):
        self._car_rel_x = self.clamp(x, -1, 1)

    @property
    def car_rel_y(self):
        return self._car_rel_y

    @car_rel_y.setter
    def car_rel_y(self, y):
        self._car_rel_y = self.clamp(y, -1, 1)

    # Safety flags
    car_unknown: bool = False  # car out of frame
    stop_following: bool = False  # emergency stop

    # Current values of angles, from -100 to 100 (essentially a % of the set max value)
    # Use properties to ensure ints in range [-100,100]
    _roll: int = 0
    _pitch: int = 0
    _yaw: int = 0

    @property
    def roll(self):
        return self._roll

    @roll.setter
    def roll(self, x):
        self._roll = int(self.clamp(x, -100, 100))

    @property
    def pitch(self):
        return self._pitch

    @pitch.setter
    def pitch(self, x):
        self._pitch = int(self.clamp(x, -100, 100))

    @property
    def yaw(self):
        return self._yaw

    @yaw.setter
    def yaw(self, x):
        self._yaw = int(self.clamp(x, -100, 100))

    def __init__(self, max_tilt: int = 5, max_height: int = 2, max_rotation_speed: int = 300, num_retries: int = 10):
        """
        :param max_tilt: maximum tilt angle, related to max speed
        :param max_height: height in metres
        """
        super().__init__()

        # create shared point object to store coordinates
        self.point = Point.Point()

        # Should scaling mechanism be proportional to height of drone?
        # Should we set scale here?
        # Try to connect, do nothing on connection failure to allow connection from interface
        self.connected = self.connect(num_retries)

        # Set safety limits
        if self.connected:
            self.set_max_tilt(max_tilt)  # proxy for max speed
            self.set_max_altitude(max_height)  # in metres
            self.set_max_tilt_rotation_speed(max_rotation_speed)  # degrees/s
            self.pan_tilt_camera(-90, 0)  # Point the camera down

        # TODO - Must make sure the camera is always pointing down - even when the drone is at an angle

    def atakeoff(self):
        # TODO: combine connected and connection.is_connected, redundant
        if self.connected or self.drone_connection.is_connected:
            self.safe_takeoff(10)
            started_updating_coords = False
            self.fly_direct(0, 0, 0, 100, 0.15)
        else:
            raise DroneNotConnectedException("Drone not connected yet")

    started_updating_coords = False

    # One option for updating the coordinates of the car's relative position.
    # Can be called by the image recognition area.
    # Alternatively can retrieve most up to date version of coordinates from the image recognition file.
    def update_coords(self, new_x, new_y):
        """if self.started_updating_coords:
            #new_modulus = math.sqrt(new_x ** 2 + new_y ** 2)
            #current_modulus = math.sqrt(self.car_rel_x ** 2 + self.car_rel_y ** 2)
            difference = new_modulus - current_modulus
            #if difference > 0.4:
            #   return
        """
        if new_x < -1 or new_x > 1 or new_y < -1 or new_y > 1:  # Invalid coordinates for the car - treat is as unknown location
            # self.car_unknown = True
            self.car_rel_x = 0
            self.car_rel_y = 0
            return
        self.car_unknown = False
        self.car_rel_x = new_x
        self.car_rel_y = new_y
        # self.set_user_sensor_callback(self.update_battery)

    def update_battery(self, sensor_dictionary):
        print("Sensors: ", sensor_dictionary)

    def battery_check(self):
        self.ask_for_state_update()
        return self.sensors.battery

    # For emergency manual override
    def immediate_land(self):

        self.stop_following = True
        time.sleep(self.movement_gap)
        self.hover()  # Go to level flight

        self.safe_land(5)

    # TODO: move to another 'utils' module?
    @staticmethod
    def clamp(n, minn, maxn):
        return max(min(maxn, n), minn)

    # Given one of the coordinates, return the speed required to move in that direction.
    # Returned value is percentage of maximum tilt angle (-100 to 100). May be scaled elsewhere
    @staticmethod
    def calculate_speed(coord: float) -> float:
        # Using equation:
        #   y = 100 * sqrt(1 - (x-1)^2) for 0 < x < 1
        # For values -1 < 1, this formula in used
        #   y = x/|x| * sqrt(1 - (|x|-1)^2) for -1 < x < 1

        # Alternative functions available:
        #   y = 100 * sin(pi/2 * x)

        # speed = 100 * math.sqrt(1 - (abs(coord) - 1) ** 2)
        """if abs(coord) < 0.15:
            print("AUFIAUSHDUKANDGYFSJKADVAWKDGVAISCHGDV ASIGASDUGASVDAS")
            return 0"""
        speed = 100 * math.sin((math.pi / 2) * coord)
        return speed
        """if coord < 0:
            return speed * -1
        else:
            return speed"""

    def sleep(self, time_length):
        self.smart_sleep(time_length)

    def move(self, vertical_movement):
        """

        :param vertical_movement: vertical speed as a percentage of maximum vertical speed
        """
        if not self.drone_connection.is_connected:
            raise DroneNotConnectedException("Disconnected while moving")
        # TODO - Wait until has been at 0 for a few time periods?
        """if self.roll == 0 and self.pitch == 0 and self.yaw == 0:
            self.flat_trim(0)
        else:
            self.fly_direct(self.roll, self.pitch, self.yaw, vertical_movement=int(vertical_movement),
                            duration=self.movement_gap)"""
        self.fly_direct(self.roll, self.pitch, self.yaw, vertical_movement=int(vertical_movement),
                        duration=self.movement_gap)

    def hover(self):
        self.pitch = 0
        self.roll = 0
        self.yaw = 0
        self.flat_trim(0)

    # TODO - delete / move this to a testing function file
    def slowdown(self, x, duration):
        print([i * 0.01 for i in range(int(10000 * x), -int(10000 * x) - 1, -int(100 * x))])
        for i in [i * 0.01 for i in range(int(10000 * x), -1, - int(100 * x))]:
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
            if self.stop_following:
                break
            # TODO - This calls find_car too many times
            if self.car_unknown:
                if not self.finding_car:
                    self.finding_car = True
                    self.find_car()
                continue
            if not self.drone_connection.is_connected:
                raise DroneNotConnectedException("Drone disconnected while following")

            # Check pyparrot documentation for this

            # v. naive
            # could be replaced by more sophisticated algorithm e.g. PID

            # Travel in right direction, and turn to face car at the same time
            # Spin quickly so that drone flies forwards as much as possible

            # print(self.calculate_speed(self.car_rel_x) * self.scale_factor)
            # self.roll = self.calculate_speed(self.car_rel_x) * self.scale_factor
            # self.pitch = self.calculate_speed(self.car_rel_y) * self.scale_factor
            predicted_x = self.car_rel_x + (
                        (self.car_rel_x - self.prev_car_rel_x) * (self.video_delay / self.movement_gap))
            predicted_y = self.car_rel_y + (
                        (self.car_rel_y - self.prev_car_rel_y) * (self.video_delay / self.movement_gap))
            #print("Current relative:", self.car_rel_x, self.car_rel_y)
            #print("Old relative:    ", self.prev_car_rel_x, self.prev_car_rel_y)
            #print("Predicted:", predicted_x, predicted_y)
            print("Predicted: %.3f %.3f" % (predicted_x, predicted_y))
            self.roll = self.calculate_speed(predicted_x) * self.scale_factor
            self.pitch = self.calculate_speed(predicted_y) * self.scale_factor

            self.prev_car_rel_x = self.car_rel_x
            self.prev_car_rel_y = self.car_rel_y

            self.started_updating_coords = True

            # Divide by pi to get value in range -1 -to 1
            # TODO - make sure this gets tested... May need quicker rotation than this
            # self.yaw = self.calculate_speed(math.atan2(self.car_rel_x, self.car_rel_y) / math.pi)
            # print(self.car_rel_x, self.car_rel_y)
            # print(self.pitch, self.roll, self.yaw)
            # TODO - move vertical movement to a global variable??
            self.move(0)

            # Care using time.sleep or drone.safe_sleep()
            # Check pyparrot documentation for this
            self.sleep(self.movement_gap)

    # In the event that the car cannot be found in the image
    # this method can be called and the drone can try and find the car.
    # Options:  fly upwards to increase field of view.
    #           Raise the angle of the camera slightly and spin around to find it
    #               Then gradually return the camera to its original vertically down angle.
    def find_car(self, timeout: int = 5):
        """

        :param timeout: time in seconds before which we
        """
        # Become stationary in non-vertical axes
        self.hover()

        time.sleep(0.5)  # Allow the drone to enter level flight

        # ASSUME: car_unknown will be set to false once we are in range of the car, so this method wont be called

        # Fly vertically upwards while slowly spinning

        # TODO: add a check on altitude to make sure we dont go above it? - Does max altitude work
        # TODO: experiment with vertical speed and spinning (yaw) speed
        # TODO : experiment with raising the camera angle to see more area
        self.yaw = 5
        while True:
            if not self.car_unknown:
                self.finding_car = False
                break
            self.move(3)  # set vertical speed to 3% of max vertical speed
            time.sleep(self.movement_gap)

    """# update point object to set new coords in a thread-safe manner
    def updatePoint(self, nx, ny):
        self.point.set(nx, ny)
        self._car_rel_x, self._car_rel_y = self.point.get()"""


if __name__ == "__main__":
    d = FollowingDrone(num_retries=1)
