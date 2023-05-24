from yolo import *
import time

yolo = Yolo("")

t = time.time()
res = yolo.get_bounding_boxes_image(cv2.imread("test_image.jpg"))
#cv2.imshow("", res)
#cv2.destroyAllWindows()

print(time.time() - t)
print(cv2.getBuildInformation())
