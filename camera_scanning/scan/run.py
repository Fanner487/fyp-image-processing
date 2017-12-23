import threading
import time
from processing.qr import get_qr_code
from processing.ocr import get_time
from processing.scan import scan_image
import cv2


# Thread function
def extract_code_and_time(file):

    print 'Thread for: ' + file

    if scan_image(file):

    	qr_code = get_qr_code(file)

    	if qr_code:

    		found, date_result, time_result = get_time(file)

    		if found:
    			print "\n\nDate: " + date_result
    			print "Time: " + time_result
    			print "QR code:" + qr_code + "\n"

    		else:
    			print "**Error reading time**"
    			print "Date: " + date_result
    			print "Time: " + time_result
    			print "QR code: " + qr_code
    	else:
    		print "QR not detected"

    else:
    	print "Screen not detected"

    return


camera = cv2.VideoCapture(2)
counter = 0

while True:

	time.sleep(0.5)

	time_epoch = str(int(time.time()))
	# image_path = "images/" + time_epoch + ".jpg"
	image_path = "images/" + str(counter) + ".jpg"

	print "Taking photo: " + str(image_path)

	(grabbed, image) = camera.read()

	cv2.imshow('f',image)
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break
	cv2.imwrite(image_path, image)

	

	t = threading.Thread(target=extract_code_and_time, args=[str(counter)])
	t.start()

	counter += 1
