from qrtools import QR

# Scans QR code and returns data (username and event ID)
def get_qr_code(image_name):

	scans_dir = u"scans/"
	codes_dir = u"codes/"

	input_scan_path = scans_dir + image_name + u"-result.jpg"

	qr_code = QR(filename=input_scan_path)
	
	if qr_code.decode():

		return qr_code.data

	else:

		return None


	
