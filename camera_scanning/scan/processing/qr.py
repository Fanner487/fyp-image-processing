from qrtools import QR
import time 


def get_qr_code(image_name):

	scans_dir = u"scans/"
	codes_dir = u"codes/"

	input_scan_path = scans_dir + image_name + u"-result.jpg"

	start_time = time.time()
	qr_code = QR(filename=input_scan_path)
	
	print "QR: --- %s seconds ---" % (time.time() - start_time)

	if qr_code.decode():

		return qr_code.data

	else:

		return None


	
