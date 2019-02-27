from PIL import Image, ImageDraw
import numpy


# Take an image and locate the area with the highest density of red pixels in

class CarFinder:
    # A pixel is accepted as red if its r > red, and g, b, < green, blue
    ACCEPTED_COLOUR = {"red": 100,
                       "green": 200,
                       "blue": 100}
    # The target only returns as found if one of the grid values is higher than this.
    # Prevents a location being returned if object not in image
    MINIMUM_ACCEPTANCE_VALUE = 0

    SCALE_RATIO = 8

    grid = []
    width, height = None, None

    @staticmethod
    def accept_colour(pixel):
        """if (pixel[0] < ACCEPTED_COLOUR["red"] and pixel[1] > ACCEPTED_COLOUR["green"] and pixel[2] < ACCEPTED_COLOUR["blue"])\
                or (pixel[1] - pixel[0] > 70 and pixel[1] - pixel[2] > 70):
            return True"""
        if (pixel[1] > 180):
            return True
        return False

    def increase_grid(self, row, col):
        grid = self.grid
        grid[row][col] += 1
        if (row - 1) >= 0:
            if (col - 1) >= 0:
                grid[row][col] += grid[row - 1][col - 1]
                grid[row - 1][col - 1] += 1
            if (col + 1) < self.width:
                grid[row][col] += grid[row - 1][col + 1]
                grid[row - 1][col + 1] += 1
        if (row + 1) < self.height:
            if (col - 1) >= 0:
                grid[row][col] += grid[row + 1][col - 1]
                grid[row + 1][col - 1] += 1
            if (col + 1) < self.width:
                grid[row][col] += grid[row + 1][col + 1]
                grid[row + 1][col + 1] += 1

    def max_value(self):
        best_coords = (-1.1, -1.1)  # Returns invalid coordinate if no best found
        best_value = self.MINIMUM_ACCEPTANCE_VALUE  # Grid value must beat this to be accepted
        for x in range(self.width):
            for y in range(self.height):
                grid_value = self.grid[y][x]
                if grid_value > best_value:
                    best_value = grid_value
                    best_coords = (x, y)
        return best_coords

    def convert_coords_to_rel(self, real_coords):
        real_x, real_y = real_coords
        half_height = self.height / 2.0
        half_width = self.width / 2.0

        x = (real_x - half_width) / half_width
        y = (half_height - real_y) / half_height
        return x, y

    def get_shrunken_pixels(self, im):

        pixels = list(im.getdata())
        new_pixels = []

        initial_width, initial_height = im.size
        new_width, new_height = initial_width // self.SCALE_RATIO, initial_height // self.SCALE_RATIO

        for r in range(0, initial_height, 8):
            for c in range(0, initial_width, 8):
                pixel = pixels[r * initial_width + c]
                new_pixels.append(pixel)
        # im2 = Image.new(im.mode, (width // 8, height // 8))
        # im2.putdata(new_pixels)
        # im2.show()
        return new_pixels, new_width, new_height

    # Creates a grid of values the same size as the image
    def reset_grid(self):
        self.grid = []
        for i in range(self.height):
            new_row = [0] * self.width
            self.grid.append(new_row)

    @staticmethod
    def average_coordinates(coord_list):
        sum_x = sum([x for x, y in coord_list])
        sum_y = sum([y for x, y in coord_list])
        avg_x = sum_x / len(coord_list)
        avg_y = sum_y / len(coord_list)
        return avg_x, avg_y

    def find_car(self, numpy_image):
        pil_image = Image.fromarray(numpy_image.astype('uint8'))
        pixels, self.width, self.height = self.get_shrunken_pixels(pil_image)

        self.reset_grid()
        for r in range(self.height):
            for c in range(self.width):
                pixel = pixels[r * self.width + c]
                pixel = (pixel[2], pixel[1], pixel[0])  # Correct the BGR to RGB
                accept_pixel = self.accept_colour(pixel)
                if accept_pixel:
                    self.increase_grid(r, c)

        highest_grid_position1 = self.max_value()

        # Run across the image in the opposite direction and average the two highest values.
        self.reset_grid()
        for r in range(self.height - 1, -1, -1):
            for c in range(self.width - 1, -1, -1):
                pixel = pixels[r * self.width + c]
                pixel = (pixel[2], pixel[1], pixel[0])  # Correct the BGR to RGB
                accept_pixel = self.accept_colour(pixel)
                if accept_pixel:
                    self.increase_grid(r, c)

        highest_grid_position2 = self.max_value()

        rel_coords = self.convert_coords_to_rel(
            self.average_coordinates([highest_grid_position1, highest_grid_position2]))
        return rel_coords


if __name__ == "__main__":
    test_image = Image.open("IMG_0404.jpg")
    # image2.show()
    np_image = numpy.array(test_image.getdata()).reshape(test_image.size[1], test_image.size[0], 3)

    car_finder = CarFinder()
    x, y = car_finder.find_car(np_image)
    w2, h2 = car_finder.width / 2, car_finder.height / 2
    print("X and Y: ", x, y)

    draw = ImageDraw.Draw(test_image)
    original_x = int(x * w2 + w2) * 8
    original_y = int(h2 - y * h2) * 8
    print(original_x, original_y)
    r = 10

    draw.ellipse((original_x - r, original_y - r, original_x + r, original_y + r), fill=(255, 0, 0, 255))
    test_image.show()
