import imutils
import numpy as np
import argparse
import cv2
import os


def scan_image(file):

	images_dir = "images/"
	scans_dir = "scans/"
	input_file = images_dir + file + ".jpg"

	print "\nScanning image: " + input_file + "\n"
	
	# load the image and compute the ratio of the old height
	# to the new height, clone it, and resize it
	image = cv2.imread(input_file)
	ratio = image.shape[0] / 500.0
	original = image.copy()
	image = imutils.resize(image, height = 500)

	edged = find_edges(image)
	 
	# show the original image and the edge detected image
	print "** Finding screen **"

	# Get contours and find best contour for screen
	contours = find_contours(edged.copy())
	screen_contour, contour_width, contour_height = find_screen_contour(contours)
	

	# If contour area larger than a rectangle in the QR code, transform the image and write to file 
	if contour_not_in_qr_code(contour_height, contour_width):

		print "** Screen found. Writing image to file**"

		# apply the four point transform to obtain a top-down
		# view of the original image
		warped = four_point_transform(original, screen_contour.reshape(4, 2) * ratio)

		output = scans_dir + file + "-result.jpg"

		if not os.path.exists(scans_dir):
			os.makedirs(scans_dir)
				
	
		cropped = blur_remove_edges_from_screen(warped)

		cv2.imwrite(output, imutils.resize(cropped, height = 650))

		if os.path.exists(input_file):
			os.remove(input_file)

		return True
			
	else:

		print "Screen not found"

		if os.path.exists(input_file):
			os.remove(input_file)

		return False


def find_screen_contour(contours):

	screen_contour = 0
	contour_height = 0
	contour_width = 0

	# loop over the contours
	for c in contours:

		# approximate the contour
		# Calculates contour perimeter
		peri = cv2.arcLength(c, True)
		# approximates polygonal curves with specified precision
		approx = cv2.approxPolyDP(c, 0.02 * peri, True)
	 
		# if our approximated contour has four points, then we
		# can assume that we have found our screen
		if len(approx) == 4:

			screen_contour = approx

			x, y, contour_width, contour_height = cv2.boundingRect(c)

			# print "Size: " + str((contour_width * contour_height))

			# Break if found
			break

	return screen_contour, contour_width, contour_height



# Blur grey image and find edges 
def find_edges(image):

	sigma_size = 5
	border_type = 0

	min_val = 75
	max_val = 200

	image_grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	image_grey = cv2.GaussianBlur(image_grey, (sigma_size, sigma_size), border_type)
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



# removes edge pixels of image
def blur_remove_edges_from_screen(image):

	image_height, image_width, _ = image.shape
	pixel_length = 10

	# May not need blurring
	# blurred = cv2.GaussianBlur(image, (5,5), 0)


	result = image[pixel_length:image_height - pixel_length, pixel_length:image_width - pixel_length]

	return result

def order_points(pts):
	
	# initialzie a list of coordinates that will be ordered
	# such that the first entry in the list is the top-left,
	# the second entry is the top-right, the third is the
	# bottom-right, and the fourth is the bottom-left
	rect = np.zeros((4, 2), dtype = "float32")
 
	# the top-left point will have the smallest sum, whereas
	# the bottom-right point will have the largest sum
	sum_points = pts.sum(axis = 1)
	rect[0] = pts[np.argmin(sum_points)]
	rect[2] = pts[np.argmax(sum_points)]
 
	# now, compute the difference between the points, the
	# top-right point will have the smallest difference,
	# whereas the bottom-left will have the largest difference
	difference = np.diff(pts, axis = 1)
	rect[1] = pts[np.argmin(difference)]
	rect[3] = pts[np.argmax(difference)]
 
	# return the ordered coordinates
	return rect

def four_point_transform(image, pts):
	# obtain a consistent order of the points and unpack them
	# individually
	rect = order_points(pts)
	(top_left, top_right, bottom_right, bottom_left) = rect
 
	# compute the width of the new image, which will be the
	# maximum distance between bottom-right and bottom-left
	# x-coordiates or the top-right and top-left x-coordinates
	width_a = np.sqrt(((bottom_right[0] - bottom_left[0]) ** 2) + ((bottom_right[1] - bottom_left[1]) ** 2))
	width_b = np.sqrt(((top_right[0] - top_left[0]) ** 2) + ((top_right[1] - top_left[1]) ** 2))
	max_width = max(int(width_a), int(width_b))
 
	# compute the height of the new image, which will be the
	# maximum distance between the top-right and bottom-right
	# y-coordinates or the top-left and bottom-left y-coordinates
	height_a = np.sqrt(((top_right[0] - bottom_right[0]) ** 2) + ((top_right[1] - bottom_right[1]) ** 2))
	height_b = np.sqrt(((top_left[0] - bottom_left[0]) ** 2) + ((top_left[1] - bottom_left[1]) ** 2))
	max_height = max(int(height_a), int(height_b))
 
	# now that we have the dimensions of the new image, construct
	# the set of destination points to obtain a "birds eye view",
	# (i.e. top-down view) of the image, again specifying points
	# in the top-left, top-right, bottom-right, and bottom-left
	# order
	dst = np.array([
		[0, 0],
		[max_width - 1, 0],
		[max_width - 1, max_height - 1],
		[0, max_height - 1]], dtype = "float32")
 
	# compute the perspective transform matrix and then apply it
	matrix = cv2.getPerspectiveTransform(rect, dst)
	warped = cv2.warpPerspective(image, matrix, (max_width, max_height))
 
	# return the warped image
	return warped