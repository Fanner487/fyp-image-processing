from transform import four_point_transform
import imutils
import numpy as np
import argparse
import cv2
import os
import time
 

def scan_image(file):

	start_time = time.time()

	images_dir = "images/"
	scans_dir = "scans/"
	input_file = images_dir + file + ".jpg"

	print "Scanning image: " + input_file
	
	# load the image and compute the ratio of the old height
	# to the new height, clone it, and resize it
	image = cv2.imread(input_file)
	ratio = image.shape[0] / 500.0
	orig = image.copy()
	image = imutils.resize(image, height = 500)
	 
	# convert the image to grayscale, blur it, and find edges
	# in the image
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray, (5, 5), 0)
	edged = cv2.Canny(gray, 75, 200)
	 
	# show the original image and the edge detected image
	print "STEP 1: Edge Detection"



	# find the contours in the edged image, keeping only the
	# largest ones, and initialize the screen contour
	_, cnts, _ = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
	cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:5]

	screenCnt = 0


	# loop over the contours
	for c in cnts:
		# approximate the contour
		peri = cv2.arcLength(c, True)
		approx = cv2.approxPolyDP(c, 0.02 * peri, True)
	 
		# if our approximated contour has four points, then we
		# can assume that we have found our screen
		if len(approx) == 4:
			screenCnt = approx
			break
	 
	# show the contour (outline) of the piece of paper
	print "STEP 2: Find contours of paper"

	# if screenCnt > 0 :
	# cv2.drawContours(image, [screenCnt], -1, (0, 255, 0), 2)
	# cv2.imshow("Outline", image)
	# cv2.waitKey(0)
	# cv2.destroyAllWindows()




	# apply the four point transform to obtain a top-down
	# view of the original image
	warped = four_point_transform(orig, screenCnt.reshape(4, 2) * ratio)
	 
	# convert the warped image to grayscale, then threshold it
	# to give it that 'black and white' paper effect
	# warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
	# warped = threshold_local(warped, 251, offset = 10)
	# warped = cv2.adaptiveThreshold(warped, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 41, 10)
	# warped = warped.astype("uint8") * 255
	 
	# show the original and scanned images
	print "STEP 3: Apply perspective transform"
	# cv2.imshow("Original", imutils.resize(orig, height = 650))
	# cv2.imshow("Scanned", imutils.resize(warped, height = 650))
	output = scans_dir + file + "-result.jpg"

	if not os.path.exists(scans_dir):
		os.makedirs(scans_dir)
	
	# cv2.imwrite(output, imutils.resize(warped, height = 650))
	# cv2.waitKey(0)
	# cv2.destroyAllWindows()

	print "--- %s seconds ---" % (time.time() - start_time)

	# if screenCnt > 0:
		
	# else:
	# 	print "No screen detected"