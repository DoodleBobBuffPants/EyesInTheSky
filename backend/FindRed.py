from PIL import Image
import numpy

# Take an image and locate the area with the highest density of red pixels in

# A pixel is accepted as red if its r > red, and g, b, < green, blue
ACCEPTED_COLOUR = {"red":   200,
                   "green": 100,
                   "blue":  100}
# The target only returns as found if one of the grid values is higher than this.
# Prevents a location being returned if object not in image
MINIMUM_ACCEPTANCE_VALUE = 0

grid = []
width, height = None, None

def accept_colour(pixel):
    if (pixel[0] > ACCEPTED_COLOUR["red"] and pixel[1] < ACCEPTED_COLOUR["green"] & pixel[2] and ACCEPTED_COLOUR["blue"])\
            or (pixel[0] - pixel[1] > 70 and pixel[0] - pixel[2] > 70):
        return True
    return False


def increase_grid(row, col):
    grid[row][col] += 2
    if (row - 1) >= 0:
        if (col - 1) >= 0:
            grid[row][col] += grid[row - 1][col - 1]
            grid[row - 1][col - 1] += 1
        if (col + 1) < width:
            grid[row][col] += grid[row - 1][col + 1]
            grid[row - 1][col + 1] += 1
    if (row + 1) < height:
        if (col - 1) >= 0:
            grid[row][col] += grid[row + 1][col - 1]
            grid[row + 1][col - 1] += 1
        if (col + 1) < width:
            grid[row][col] += grid[row + 1][col + 1]
            grid[row + 1][col + 1] += 1

def max_value():
    best_coords = (-1.1, -1.1) # Returns invalid coordinate if no best found
    best_value = MINIMUM_ACCEPTANCE_VALUE # Grid value must beat this to be accepted
    for x in range(width):
        for y in range(height):
            grid_value = grid[y][x]
            if grid_value > best_value:
                best_value = grid_value
                best_coords = (x, y)
    return best_coords


def find_red(image):
    global grid, width, height
    img = Image.fromarray(image.astype('uint8'))
    #img.show()
    pixels = list(img.getdata())
    width, height = img.size
    # Creates a grid of values the same size as the image For every pixel in the image, if it is red enough then add
    # 2 to the corresponding space in the grid. Also add 1 to each of the spaces adjacent to that.


    grid = []
    for i in range(height):
        new_row = [0] * width
        grid.append(new_row)

    #img.show()
    for r in range(height):
        for c in range(width):
            pixel = pixels[r * width + c]
            pixel = (pixel[2], pixel[1], pixel[0])
            #print(r, c, pixel)
            accept_pixel = accept_colour(pixel)
            if accept_pixel:
                #print(r, c)
                increase_grid(r, c)

    return max_value()




if __name__ == "__main__":

    image2 = Image.open("IMG_0398.jpg")
    #image2.show()
    np_image = numpy.array(image2.getdata()).reshape(image2.size[1], image2.size[0], 3)


    x, y = find_red(np_image)
    w, h = width / 2, height / 2
    print("X and Y: ", x, y)
    print(w, h)
    print((x - w)/w, (h - y)/h)
