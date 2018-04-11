import imutils
import numpy as np
import argparse
import cv2
import os


def scan_image(file):

	images_dir = "images/"
	scans_dir = "scans/"
	test_dir = "test-images/"
	input_file = images_dir + file + ".jpg"

	# print "\nScanning image: " + input_file + "\n"
	
	# load the image and compute the ratio of the old height
	# to the new height, clone it, and resize it
	image = cv2.imread(input_file)
	ratio = image.shape[0] / 500.0
	original = image.copy()
	image = imutils.resize(image, height = 500)

	edged = find_edges(image)


	# Gets contour most matched to a rectangle (screen)
	contours = find_contours(edged.copy())

	screen_contour, contour_width, contour_height = find_screen_contour(contours, file, image)

	# If contour area larger than a rectangle in the QR code, transform the image and write to file 
	if contour_not_in_qr_code(contour_height, contour_width):

		# print "** Screen found. Writing image to file**"

		# Take image and reshape into a rectangle 
		warped = reshape_screen(original, screen_contour.reshape(4, 2) * ratio)

		output = scans_dir + file + "-result.jpg"

		if not os.path.exists(scans_dir):
			os.makedirs(scans_dir)
	
		# Removes jagged noise from the edges of the screen
		# and blurs image for faster processing
		cropped = blur_remove_edges_from_screen(warped, file)

		cv2.imwrite(output, imutils.resize(cropped, height = 650))

		if os.path.exists(input_file):
			os.remove(input_file)

		return True
			
	else:

		# print "Screen not found"

		if os.path.exists(input_file):
			os.remove(input_file)

		return False


def find_screen_contour(contours, file, image):

	screen_contour = 0
	contour_height = 0
	contour_width = 0

	# loop over the contours which finds best match for rectangle i.e screen
	for c in contours:
		
		# Calculates contour perimeter
		# and approximates contour using perimeter
		perimeter = cv2.arcLength(c, True)
		# approximates polygonal curves with specified precision
		approx = cv2.approxPolyDP(c, 0.02 * perimeter, True)

		# If contour has 4 points, then the screen is found
		if len(approx) == 4:

			screen_contour = approx

			x, y, contour_width, contour_height = cv2.boundingRect(c)
			image_copy = image.copy()

			break

		
		

	return screen_contour, contour_width, contour_height



# Blur grey image and find edges 
def find_edges(image):

	border_type = 0
	sigma = 5
	min_val = 75
	max_val = 200

	image_grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	image_grey = cv2.GaussianBlur(image_grey, (sigma, sigma), border_type)
	edged = cv2.Canny(image_grey, min_val, max_val)


	return edged

# Find contours and sort in descending order by size
def find_contours(image):
	_, contours, _ = cv2.findContours(image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
	contours = sorted(contours, key = cv2.contourArea, reverse = True)[:5]

	return contours


# Checks if the contour picked up bigger than square of QR code in pixel to determine screen
def contour_not_in_qr_code(height, width):

	length = 100

	threshold_area = length * length
	contour_area = height * width

	if contour_area > threshold_area:
		return True
	else:
		return False



# removes edge pixels of image and resizes it.
def blur_remove_edges_from_screen(image, file):

	image_height, image_width, _ = image.shape
	pixel_length = 10

	# May not need blurring
	# blurred = cv2.GaussianBlur(image, (5,5), 0)

	result = image[pixel_length:image_height - pixel_length, pixel_length:image_width - pixel_length]

	return result


def order_points(points):
	
	# empty array which will be ordered where [0]
	# entry in the list is the top-left, [1] is top-right
	# [2] is bottom-right and [3] is bottom-left
	rect = np.zeros((4, 2), dtype = "float32")
 
	# Calculate top-left point which will have smallest sum,
	# bottom right will have largest sum
	sum_points = points.sum(axis = 1)
	rect[0] = points[np.argmin(sum_points)]
	rect[2] = points[np.argmax(sum_points)]

	# Top right will have smallest difference
	# bottom will have largest difference
	difference = np.diff(points, axis = 1)
	rect[1] = points[np.argmin(difference)]
	rect[3] = points[np.argmax(difference)]
 
	# return the ordered coordinates
	return rect

def reshape_screen(image, points):

	# obtain a consistent order of the points and unpack them
	# individually
	rect = order_points(points)
	(top_left, top_right, bottom_right, bottom_left) = rect

	# Calculates width of new image by getting (max dist between bottom-side right and left or top-side right and left)
	width_a = np.sqrt(((bottom_right[0] - bottom_left[0]) ** 2) + ((bottom_right[1] - bottom_left[1]) ** 2))
	width_b = np.sqrt(((top_right[0] - top_left[0]) ** 2) + ((top_right[1] - top_left[1]) ** 2))
	max_width = max(int(width_a), int(width_b))
 
	# Calculates height of new image by getting (max dist between left top and bottom or right-side top and bottom)
	height_a = np.sqrt(((top_right[0] - bottom_right[0]) ** 2) + ((top_right[1] - bottom_right[1]) ** 2))
	height_b = np.sqrt(((top_left[0] - bottom_left[0]) ** 2) + ((top_left[1] - bottom_left[1]) ** 2))
	max_height = max(int(height_a), int(height_b))
 
	# New array with dimensions of new image as rectangle
	# This array will warp "birds-eye" view of screen into top down view
	dst = np.array([
		[0, 0],
		[max_width - 1, 0],
		[max_width - 1, max_height - 1],
		[0, max_height - 1]], 
		dtype = "float32")
 
	# Calculates perspective transform matrix and then applies warp persective for resulting picture
	matrix = cv2.getPerspectiveTransform(rect, dst)
	warped = cv2.warpPerspective(image, matrix, (max_width, max_height))
 
	return warped