"""road_lane_detection.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1w6xv6v5xuQPmMJMMQ5MZnGlC6F9bsi7Q
"""

# ROAD LANE DETECTION

import cv2
import matplotlib.pyplot as plt
import numpy as np

# parameters
slopecutoff = 0.5
#image_name = "um_000006.png"

#image_path = "content/" + image_name
#image1 = cv2.imread(image_path)
#plt.imshow(image1)

def Hsv(image):
    image = np.asarray(image)
    return cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

def Grey(image):
    # convert to grayscale
    image = np.asarray(image)
    return cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

def White(hsv):
    lower_white = np.array([0, 0, 128], dtype=np.uint8)
    upper_white = np.array([0, 0, 255], dtype=np.uint8)

    # Threshold the HSV image to get only white colors
    return cv2.inRange(hsv, lower_white, upper_white)

def Yellow(hsv):
    lower_yellow = np.array([15, 50, 127], dtype=np.uint8)
    upper_yellow = np.array([25, 100, 255], dtype=np.uint8)

    # Threshold the HSV image to get only white colors
    return cv2.inRange(hsv, lower_yellow, upper_yellow)

# Apply Gaussian Blur --> Reduce noise and smoothen image
def gauss(image):
    return cv2.GaussianBlur(image, (5, 5), 0)


# outline the strongest gradients in the image --> this is where lines in the image are
def canny(image):
    edges = cv2.Canny(image, 50, 150)
    return edges


def region(image):
    height, width = image.shape
    # isolate the gradients that correspond to the lane lines
    triangle = np.array([
        [(0, height), (int(width / 2), int(height / 4)), (width, height)]
    ])
    # create a black image with the same dimensions as original image
    mask = np.zeros_like(image)
    # create a mask (triangle that isolates the region of interest in our image)
    mask = cv2.fillPoly(mask, triangle, 255)
    mask = cv2.bitwise_and(image, mask)
    #cv2.imshow("mask", mask)
    return mask


def display_lines(image, lines):
    lines_image = np.zeros_like(image)
    # make sure array isn't empty
    if lines is not None:
        if len(lines.shape) > 1:
            for line in lines:
                x1, y1, x2, y2 = line
                # draw lines on a black image
                cv2.line(lines_image, (x1, y1), (x2, y2), (255, 0, 0), 10)
        else:
            x1, y1, x2, y2 = lines
            cv2.line(lines_image, (x1, y1), (x2, y2), (255, 0, 0), 10)
    return lines_image


def average(image, lines):
    left = []
    right = []

    if lines is not None:
        for line in lines:
            #print(line)
            x1, y1, x2, y2 = line.reshape(4)
            # fit line to points, return slope and y-int
            parameters = np.polyfit((x1, x2), (y1, y2), 1)
            #print(parameters)
            slope = parameters[0]
            y_int = parameters[1]
            # lines on the right have positive slope, and lines on the left have neg slope
            if -slopecutoff > slope or slope > slopecutoff:  # uses param slopecutoff to filter bad lines
                if slope < 0:
                    left.append((slope, y_int))
                else:
                    right.append((slope, y_int))

    # takes average among all the columns (column0: slope, column1: y_int)
    if len(right) > 0:  # if there are any entries in right, compute, or assign right_line empty
        right_avg = np.average(right, axis=0)
        right_line = make_points(image, right_avg)
    else:
        right_line = []
    if len(left) > 0:  # if there are any entries in left, compute, or assign left_line empty
        left_avg = np.average(left, axis=0)
        left_line = make_points(image, left_avg)
    else:
        left_line = []

    # create lines based on averages calculates
    if len(right_line) == 0:
        return np.array(left_line)
    if len(left_line) == 0:
        return np.array(right_line)
    if len(right_line) == 0 and len(left_line) == 0:
        return np.array()

    return np.array([left_line, right_line])

def make_points(image, average):
    #print(average)
    slope, y_int = average
    y1 = image.shape[0]
    # how long we want our lines to be --> 3/5 the size of the image
    y2 = int(y1 * (3 / 5))
    # determine algebraically
    x1 = int((y1 - y_int) // slope)
    x2 = int((y2 - y_int) // slope)
    return np.array([x1, y1, x2, y2])


'''##### DETECTING lane lines in image ######'''

'''copy = np.copy(image1)
edges = cv2.Canny(copy, 50, 150)
isolated = region(edges)
cv2(edges)
cv2(isolated)
cv2.waitKey(0)

# DRAWING LINES: (order of params) --> region of interest, bin size (P, theta), min intersections needed, placeholder array,
lines = cv2.HoughLinesP(isolated, 2, np.pi / 180, 100, np.array([]), minLineLength=40, maxLineGap=5)
averaged_lines = average(copy, lines)
black_lines = display_lines(copy, averaged_lines)
# taking wighted sum of original image and lane lines image
lanes = cv2.addWeighted(copy, 0.8, black_lines, 1, 1)
cv2(lanes)
cv2.waitKey(0)
'''

def compute(image_path):
    image1 = cv2.imread(image_path)
    copy = np.copy(image1)
    grey = Grey(copy)
    hsv = Hsv(copy)
    white = White(hsv)
    yellow = Yellow(hsv)
    weighted = cv2.addWeighted(grey, 0.2, white, 1, 1)
    weighted = cv2.addWeighted(weighted, 1, yellow, 1, 1)
    # cv2.imshow("weighted", weighted)
    # gaus_grey = gauss(grey)
    # gaus_white = gauss(white)
    # gaus_yellow = gauss(yellow)
    # edges = canny(gaus_grey)
    edges = canny(weighted)
    isolated = region(edges)
    cv2.imshow("isolated", isolated)
    lines = cv2.HoughLinesP(isolated, 2, np.pi / 180, 100, np.array([]), minLineLength=40, maxLineGap=5)
    averaged_lines = average(copy, lines)
    black_lines = display_lines(copy, averaged_lines)
    lanes = cv2.addWeighted(copy, 0.8, black_lines, 1, 1)
    cv2.imwrite("content/output/" + image_name, lanes)
    cv2.waitKey(0)

image_num = 10
while image_num < 95 :
    image_name = "um_0000" + str(image_num) + ".png"
    image_path = "content/" + image_name
    compute(image_path)
    image_num += 1