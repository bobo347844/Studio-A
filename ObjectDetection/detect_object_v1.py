import numpy as np
import cv2

capture = cv2.VideoCapture(0)

index = -1
thickness = 4
color = (255, 0, 255)
kernel = np.ones((5,5), 'uint8')

while(True):
	numContours = 0
	ret, frame = capture.read()

	blur = cv2.GaussianBlur(frame, (201,201), 0)
	dilate = cv2.dilate(blur, kernel, iterations=1)
	erode = cv2.erode(dilate, kernel, iterations=1)

	gray = cv2.cvtColor(erode, cv2.COLOR_BGR2GRAY)
	thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 115, 3)
	_, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

	for c in contours:
		area = cv2.contourArea(c)

		if area > 100:
			cv2.drawContours(frame, [c], -1, color, 3)
			numContours += 1

			M = cv2.moments(c)
			cx = int( M['m10']/M['m00'])
			cy = int( M['m01']/M['m00'])
			cv2.circle(frame, (cx,cy), 4, (0,0,255), -1)

	cv2.imshow("Frame", frame)

	print(numContours)

	ch = cv2.waitKey(1000)
	if ch & 0xFF == ord('q'):
		break

capture.release()
cv2.destroyAllWindows()
