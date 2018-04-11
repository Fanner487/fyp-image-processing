import cv2
import numpy as np
import time


start_time = time.time()


img = cv2.imread("sample.jpg", 0);

circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 1, 20, param1=50,param2=30, minRadius=0, maxRadius=0)

circles = np.uint16(np.around(circles))

print("--- %s seconds ---" % (time.time() - start_time))

for i in circles[0,:]:
	cv2.circle(img,(i[0],i[1]),i[2],(0,255,0),2)
	cv2.circle(img,(i[0],i[1]),2,(0,0,255),3)

cv2.imshow('detected circles',img)
cv2.waitKey(0)
cv2.destroyAllWindows()