from yolo import *
import time
import cv2

yolo = Yolo("")

t = time.time()
#res = yolo.get_bounding_boxes(cv2.imread("test_image.jpg"))
res = cv2.imread("test_image.jpg")
print(res.shape)
#cv2.imshow("", res)
#cv2.destroyAllWindows()


#print(time.time() - t)
#print(cv2.getBuildInformation())
