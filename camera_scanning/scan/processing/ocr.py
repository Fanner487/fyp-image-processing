# import the necessary packages
from PIL import Image
import pytesseract
import cv2
import os
import time
import numpy as np

# contrast enhance, sharpen, threshold and blue image
def enhance_image(image):


	kernel = np.array([[-1,-1,-1,-1,-1],
						[-1,2,2,2,-1],
						[-1,2,8,2,-1],
	                    [-1,2,2,2,-1],
	                    [-1,-1,-1,-1,-1]]) / 8.0


	image_grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

	clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))

	image_clahe = clahe.apply(image_grey)
	
	image_sharpen= cv2.filter2D(image_clahe, -1, kernel)

	image_threshold =cv2.threshold(image_sharpen, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

	image_blur = cv2.medianBlur(image_threshold, 3)

	return image_blur

def get_time(file):

	scans_dir = "scans/"
	input_scan_path = scans_dir + file + "-result.jpg"
	percentage_of_screen = 0.33

	start_time = time.time()

	image = cv2.imread(input_scan_path)


	# Get height and width of image
	height, width, _ = image.shape

	# startY, endY, startX, endX
	# Crop top percentage of screen 
	image = image[0:int(height * percentage_of_screen), 0:width]

	enhanced = enhance_image(image)
 
	# temp file for OCR operation
	temp_file = "{}.jpg".format(os.getpid())
	cv2.imwrite(temp_file, enhanced)

	text = pytesseract.image_to_string(Image.open(temp_file))
	os.remove(temp_file)

	ret, date_result, time_result = verify_date_time(text)

	print "--- OCR: %s seconds ---" % (time.time() - start_time)

	if ret:
		return True, date_result, time_result
	else:
		return False, date_result, time_result


def get_length_and_times(input_time):

	length = 0
	hour = 0
	minute = 0
	second = 0
	
	try:

		length = len(input_time)
		hour = int(input_time[0:2])
		minute = int(input_time[3:5])
		second = int(input_time[6:length])

	except ValueError:

		print "Error parsing"

	return hour, minute, second, length


def get_length_and_date(date):

	length = 0
	day = 0
	month = 0
	year = 0
	
	try:

		length = len(date)
		day = int(date[0:2])
		month = int(date[3:5])
		year = int(date[6:length])
	except ValueError:

		print "Error parsing"

	return day, month, year, length

# Checks to see if time is valid, string is of valid length and colons are in right postion
def is_time_valid(input_time):

	hour, minute, second, length = get_length_and_times(input_time)

	if length == 8 and input_time[2] == ':' and input_time[5] == ':' and input_time.replace(":", "").isdigit() and hour < 24 and minute < 60 and second < 60:
		return True
	else: 
		return False

def is_date_valid(input_date):
	
	day, month, year, length = get_length_and_date(input_date)

	if length == 10 and input_date[2] == '/' and input_date[5] == '/' and input_date.replace("/", "").isdigit() and day < 32 and month < 13 and len(str(year)) == 4:
		return True
	else:
		return False



def clean_and_verify_time(input_time):

	if is_time_valid(input_time):

		return True, input_time

	else:

		result_time = input_time

		# Trim whitespace change for colons
		result_time = result_time.replace(" " , "")
		result_time = result_time.replace('.', ':')
		result_time = result_time.replace(',', ':')
		result_time = result_time.replace(';', ':')

		if not result_time.replace(":", "").isdigit():

			result_time = replace_characters_for_digits(result_time)
		

		if is_time_valid(result_time):

			print "After:" + result_time
			return True, result_time
		else:
			return False, result_time


def clean_and_verify_date(input_date):

	if is_date_valid(input_date):

		return True, input_date

	else:

		result_date = input_date

		# Trim whitespace change for colons
		result_date = result_date.replace(" " , "")


		if not result_date.replace("/", "").isdigit():

			result_date = replace_characters_for_digits(result_date)
		

		if is_date_valid(result_date):
			return True, result_date
		else:
			return False, result_date


def replace_characters_for_digits(input_string):

	result = input_string
	replace_dict = {
		'o': '0',
		'i': '1',
		'I': '1',
		'l': '1',
		'A': '4',
		'B': '8',
		'G': '6',
		'Z': '2',
	}

	for key, value in replace_dict.items():

		result = result.replace(key, value)

	return result 


def verify_date_time(text):

	date, time = text.split("\n")

	date_found, date_result = clean_and_verify_date(date) 
	time_found, time_result = clean_and_verify_time(time)

	if date_found and time_found:
		return True, date_result, time_result
	else:
		return False, date_result, time_result
