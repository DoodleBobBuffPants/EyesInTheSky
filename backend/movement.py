from pyparrot.Bebop import Bebop
import math
import time


class DroneException(Exception):
    pass


class DroneNotConnectedException(DroneException):
    pass


class FollowingDrone(Bebop):
    # Adjust the speed of the drone
    scale_factor = 0.1

    # Time in seconds between instructions being sent to the drone. An arbitrary choice
    movement_gap = 0.1

    # Estimated time that the video feed is delayed by
    video_delay = 0.5

    # Position of the car in relation to the drone - values in range [-1, 1]
    # Properties used to keep values in required range
    _car_rel_y: float = 0
    _car_rel_x: float = 0

    prev_car_rel_x: float = 0
    prev_car_rel_y: float = 0

    car_unknown: bool = False  # car out of frame
    finding_car: bool = False  # The procedure for finding the car is running
    stop_following: bool = False  # Function sending movement instructions to the drone will stop

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

    def __init__(self, max_tilt: int = 5, max_height: int = 2, max_rotation_speed: int = 300, num_retries: int = 3):
        """

        :param max_rotation_speed: Degrees per second that the drone can rotate at
        :param num_retries: Times to attempt to connect to the drone
        :param max_tilt: maximum tilt angle, related to max speed
        :param max_height: height in metres
        """
        super().__init__()

        # Try to connect, do nothing on connection failure to allow connection from interface
        self.connected = self.connect(num_retries)

        # Set safety limits
        if self.connected:
            self.set_max_tilt(max_tilt)  # proxy for max speed
            self.set_max_altitude(max_height)  # in metres
            self.set_max_rotation_speed(max_rotation_speed)  # degrees/s
            self.pan_tilt_camera(-90, 0)  # Point the camera down

    def drone_takeoff(self):
        if self.connected or self.drone_connection.is_connected:
            self.safe_takeoff(10)  # Timeout time
            self.fly_direct(0, 0, 0, 100, 0.15)  # Fly upwards for a period of time
        else:
            raise DroneNotConnectedException("Drone not connected yet")

    # Called by class finding the car
    def update_coords(self, new_x, new_y):
        # If received coordinates are invalid, this indicates the car is not in frame
        if new_x < -1 or new_x > 1 or new_y < -1 or new_y > 1:
            if not self.stop_following:
                self.car_unknown = True
            self.car_rel_x = 0
            self.car_rel_y = 0
            return
        self.car_unknown = False
        self.car_rel_x = new_x
        self.car_rel_y = new_y

    def battery_check(self):
        self.ask_for_state_update()
        return self.sensors.battery

    def immediate_land(self):
        self.stop_following = True
        time.sleep(self.movement_gap)
        self.hover()  # Go to level flight
        self.safe_land(5)

    @staticmethod
    def clamp(n, min_n, max_n):
        return max(min(max_n, n), min_n)

    # Given one of the coordinates, return the speed required to move in that direction.
    # Returned value is percentage of maximum tilt angle (-100 to 100). May be scaled elsewhere
    @staticmethod
    def calculate_speed(coord: float) -> float:

        # Using equation:
        #   y = 100 * sin(pi / 2 * coord)
        # Alternative function:
        #   y = x/|x| * sqrt(1 - (|x|-1)^2) for -1 < x < 1

        speed = 100 * math.sin((math.pi / 2) * coord)
        # speed = coord / abs(coord) * 100 * math.sqrt(1 - (abs(coord) - 1) ** 2)
        return speed

    def sleep(self, time_length):
        self.smart_sleep(time_length)

    def move(self, vertical_movement=0):
        """ Sends the commands to move the drone using pitch, tilt and yaw values

        :param vertical_movement: vertical speed as a percentage of maximum vertical speed
        """
        if not self.drone_connection.is_connected:
            raise DroneNotConnectedException("Disconnected while moving")

        self.fly_direct(self.roll, self.pitch, self.yaw, vertical_movement=int(vertical_movement),
                        duration=self.movement_gap)

    def hover(self):
        self.pitch = 0
        self.roll = 0
        self.yaw = 0
        self.flat_trim(0)

    # Runs in a continuous loop - Calculates required pitch/roll values and sends instructions to the drone
    # Must be run in own thread
    def follow_car(self):

        while True:
            if self.stop_following:
                break
            if self.car_unknown:
                if not self.finding_car:
                    self.finding_car = True
                    self.find_car()
                continue
            if not self.drone_connection.is_connected:
                raise DroneNotConnectedException("Drone disconnected while following")

            # Calculate movements based on current calculated position - no prediction
            # print(self.calculate_speed(self.car_rel_x) * self.scale_factor)
            # self.roll = self.calculate_speed(self.car_rel_x) * self.scale_factor
            # self.pitch = self.calculate_speed(self.car_rel_y) * self.scale_factor

            # Often have big swing backwards once drone reaches car
            # reduce the scale of the prediction when the relative coordinates are low
            # OPTION 1:
            x_scale = 1 if abs(self.car_rel_x) < 0.2 else 0.4
            y_scale = 1 if abs(self.car_rel_y) < 0.2 else 0.4

            # OPTION 2:
            # x_scale = 0.7 * abs(self.car_rel_x) + 0.3
            # y_scale = 0.7 * abs(self.car_rel_y) + 0.3

            # Assumes current video feed is slightly delayed - predicts actual current location of the car
            predicted_x = self.car_rel_x + (
                    (self.car_rel_x - self.prev_car_rel_x) * (self.video_delay / self.movement_gap) * x_scale)
            predicted_y = self.car_rel_y + (
                    (self.car_rel_y - self.prev_car_rel_y) * (self.video_delay / self.movement_gap) * y_scale)

            print("Predicted:                %.3f %.3f" % (round(predicted_x, 3), round(predicted_y, 3)))
            self.roll = self.calculate_speed(predicted_x) * self.scale_factor
            self.pitch = self.calculate_speed(predicted_y) * self.scale_factor

            self.prev_car_rel_x = self.car_rel_x
            self.prev_car_rel_y = self.car_rel_y

            self.move()

            self.sleep(self.movement_gap)

    def find_car(self):
        """ Called when car cannot be found in the image - attempts to locate car"""

        self.hover()
        time.sleep(0.5)  # Allow the drone to enter level flight

        # Spin the drone and raise the camera angle to get a bigger field of view
        self.yaw = 20
        self.pan_tilt_camera(-75, 0)
        while True:
            if not self.car_unknown:
                self.finding_car = False
                self.car_unknown = False
                self.pan_tilt_camera_velocity(self, 0, -3, duration=5)  # Slowly move the camera back to vertical
                break
            self.move(vertical_movement=3)  # set vertical speed to 3% of max vertical speed
            time.sleep(self.movement_gap)


if __name__ == "__main__":
    d = FollowingDrone(num_retries=1)
