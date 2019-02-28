from PIL import Image, ImageDraw
import numpy


# Take an image and locate the area with the highest density of red pixels in

class CarFinder:
    # This is the colour that the target is.
    # Options are red, green, blue, white
    REQUIRED_COLOUR = "red"

    # Determines what range of pixels will be accepted. e.g. REQUIRED_COLOUR = green => the pixel must have red and
    # blue values less than what is given below, but a higher green value. White required all the pixel's values
    # to be higher
    ACCEPTED_COLOUR = {"red": 200,
                       "green": 100,
                       "blue": 100}
    # Another method of testing for a correctly coloured pixel. Pixel will be accepted if the REQUIRED_COLOUR
    # component is RGB_DIFFERENCE greater than both the other pixel colour components
    RGB_DIFFERENCE = 50
    # The target only returns as found if one of the grid values is higher than this.
    # Prevents a location being returned if object not in image
    MINIMUM_ACCEPTANCE_VALUE = 1000  # TODO - Is this too big

    SCALE_RATIO = 8

    grid = []
    width, height = None, None

    def accept_colour(self, pixel):
        """ Determines whether a pixel is likely part of the car

        :rtype: boolean
        :param pixel: A pixel that will be tested whether it is valid
        :return: true/false indicating whether this pixel is likely part of the car
        """
        if self.REQUIRED_COLOUR == "white":
            if (pixel[0] > self.ACCEPTED_COLOUR["red"] and
                    pixel[1] > self.ACCEPTED_COLOUR["green"] and
                    pixel[2] > self.ACCEPTED_COLOUR["blue"]):
                return True
        elif self.REQUIRED_COLOUR == "red":
            if (pixel[0] > self.ACCEPTED_COLOUR["red"] and
                    pixel[1] < self.ACCEPTED_COLOUR["green"] and
                    pixel[2] < self.ACCEPTED_COLOUR["blue"]):
                return True
            if pixel[0] - pixel[1] > self.RGB_DIFFERENCE and pixel[0] - pixel[2] > self.RGB_DIFFERENCE:
                return True
        elif self.REQUIRED_COLOUR == "green":
            if (pixel[0] < self.ACCEPTED_COLOUR["red"] and
                    pixel[1] > self.ACCEPTED_COLOUR["green"] and
                    pixel[2] < self.ACCEPTED_COLOUR["blue"]):
                return True
            if pixel[1] - pixel[0] > self.RGB_DIFFERENCE and pixel[1] - pixel[2] > self.RGB_DIFFERENCE:
                return True
        elif self.REQUIRED_COLOUR == "blue":
            if (pixel[0] < self.ACCEPTED_COLOUR["red"] and
                    pixel[1] < self.ACCEPTED_COLOUR["green"] and
                    pixel[2] > self.ACCEPTED_COLOUR["blue"]):
                return True
            if pixel[2] - pixel[0] > self.RGB_DIFFERENCE and pixel[2] - pixel[1] > self.RGB_DIFFERENCE:
                return True

        return False

    def increase_grid(self, row: int, col: int):
        """ Increase the value of grid[row][col] by 1 and add to it the value of its four adjacent cells in the grid

        :rtype: None
        :param row: row in the grid to be increased
        :param col: column in the grid to be increased
        """
        grid = self.grid
        grid[row][col] += 1

        if (row - 1) >= 0:
            if (col - 1) >= 0:
                grid[row][col] += grid[row - 1][col - 1]
            if (col + 1) < self.width:
                grid[row][col] += grid[row - 1][col + 1]

        if (row + 1) < self.height:
            if (col - 1) >= 0:
                grid[row][col] += grid[row + 1][col - 1]
            if (col + 1) < self.width:
                grid[row][col] += grid[row + 1][col + 1]

    def max_value(self):
        """ Returns the position, (x, y), of the highest valued cell in grid. Returns invalid coordinates if a high
        enough value is not found

        :rtype: (int, int)
        :return: location, (x,y), of the cell in grid with the highest value. (0, 0) top left
        """
        best_coords = (-1.1, -1.1)  # Returns invalid coordinate if no best found # TODO - try this at -1 instead
        best_value = self.MINIMUM_ACCEPTANCE_VALUE  # Grid value must beat this to be accepted
        for x in range(self.width):
            for y in range(self.height):
                grid_value = self.grid[y][x]
                if grid_value > best_value:
                    best_value = grid_value
                    best_coords = (x, y)
        print(best_value)
        return best_coords

    def convert_to_relative(self, real_coords: (int, int)) -> (float, float):
        """ Takes coordinates of a location in the grid/image and returns the relative position of those coordinates
        in the full grid/image

        :rtype: (x, y)
        :param real_coords: (x, y) coordinates with origin top-left
        :return: Scaled coordinates in the range [-1, 1].
        """
        real_x, real_y = real_coords
        half_height = self.height / 2.0
        half_width = self.width / 2.0

        x = (real_x - half_width) / half_width
        y = (half_height - real_y) / half_height
        return x, y

    def get_shrunken_pixels(self, im):
        """ Takes a PIL image and keeps every nth pixel from every nth row. n defined by SCALE_RATIO

        :rtype: int[], int, int
        :param im: PIL image
        :return: list of pixels of the reduced image, width of new image, height of new image
        """
        pixels = list(im.getdata())
        new_pixels = []

        initial_width, initial_height = im.size
        new_width, new_height = initial_width // self.SCALE_RATIO, initial_height // self.SCALE_RATIO

        for r in range(0, initial_height, self.SCALE_RATIO):
            for c in range(0, initial_width, self.SCALE_RATIO):
                pixel = pixels[r * initial_width + c]
                new_pixels.append(pixel)

        return new_pixels, new_width, new_height

    # Creates a grid of values the same size as the image
    def reset_grid(self):
        """Resets self.grid to be all 0s"""

        self.grid = []
        for i in range(self.height):
            new_row = [0] * self.width
            self.grid.append(new_row)

    @staticmethod
    def average_coordinates(coord_list):
        """

        :rtype: (int, int)
        :param coord_list: A list of (x, y) coordinates
        :return: The average of the coordinates
        """
        sum_x = sum([x for x, y in coord_list])
        sum_y = sum([y for x, y in coord_list])
        avg_x = sum_x / len(coord_list)
        avg_y = sum_y / len(coord_list)
        return avg_x, avg_y

    def find_car(self, numpy_image):
        """ Looks for the largest sized section of a particular colour

        :rtype: (float, float)
        :param numpy_image: A numpy image to look for the car in
        :return: The relative coordinates of the car in the image
        """
        pil_image = Image.fromarray(numpy_image.astype('uint8'))
        pixels, self.width, self.height = self.get_shrunken_pixels(pil_image)

        self.reset_grid()
        for r in range(self.height):
            for c in range(self.width):
                pixel = pixels[r * self.width + c]
                #pixel = (pixel[2], pixel[1], pixel[0])  # Correct the BGR to RGB # TODO - flip the pixel?
                #print(r, c, pixel)
                accept_pixel = self.accept_colour(pixel)
                if accept_pixel:
                    #print(r, c)
                    self.increase_grid(r, c)

        highest_grid_position1 = self.max_value()
        print(highest_grid_position1)

        # Run across the image in the opposite direction and average the two highest values.
        self.reset_grid()
        for r in range(self.height - 1, -1, -1):
            for c in range(self.width - 1, -1, -1):
                pixel = pixels[r * self.width + c]
                #pixel = (pixel[2], pixel[1], pixel[0])  # Correct the BGR to RGB # TODO flip the pixel?
                #print(r, c, pixel)
                accept_pixel = self.accept_colour(pixel)
                if accept_pixel:
                    #print(r, c)
                    self.increase_grid(r, c)

        highest_grid_position2 = self.max_value()
        print(highest_grid_position2)

        rel_coords = self.convert_to_relative(
            self.average_coordinates([highest_grid_position1, highest_grid_position2]))
        print(rel_coords)
        return rel_coords


if __name__ == "__main__":
    test_image = Image.open("IMG_0408.jpg")
    # image2.show()
    np_image = numpy.array(test_image.getdata()).reshape(test_image.size[1], test_image.size[0], 3)

    car_finder = CarFinder()
    x, y = car_finder.find_car(np_image)
    w2, h2 = car_finder.width / 2, car_finder.height / 2
    print("X and Y: ", x, y)

    draw = ImageDraw.Draw(test_image)
    original_x = int(x * w2 + w2) * car_finder.SCALE_RATIO
    original_y = int(h2 - y * h2) * car_finder.SCALE_RATIO
    print(original_x, original_y)
    r = 10

    draw.ellipse((original_x - r, original_y - r, original_x + r, original_y + r), fill=(0, 0, 0, 255))
    test_image.show()
