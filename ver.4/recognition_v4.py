# Import the necessary packages
from imutils.perspective import four_point_transform
import imutils, cv2, os, sys
import numpy as np

def classify():
    # returns a 2D array, where each pixel is either 0 or 255 (255 means the pixel is in the range)
    mask_red = cv2.inRange(img_hsv, LOWER_RED, UPPER_RED)
    mask_orange = cv2.inRange(img_hsv, LOWER_ORANGE, UPPER_ORANGE)
    mask_green = cv2.inRange(img_hsv, LOWER_GREEN, UPPER_GREEN)

    green_pixels = np.count_nonzero(mask_green)
    red_pixels = np.count_nonzero(mask_red)
    orange_pixels = np.count_nonzero(mask_orange)

    if green_pixels > red_pixels and green_pixels > orange_pixels:
        cv2.putText(img, "GO", (250, 250), 0, 1, (255, 255, 255), 4)
    else:
        cv2.putText(img, "STOP", (250, 250), 0, 1, (255, 255, 255), 4)
        
def scan():
    try:
        data, bbox, _ = detector.detectAndDecode(img)
        return data, bbox
    except:
        os.execl(sys.executable, os.path.abspath(__file__), *sys.argv) 

def transform():
    index_point = np.int32(bbox).reshape(4, 2)
    rect = four_point_transform(img, index_point)
    return rect

LOWER_RED = np.array([3, 60, 60])
UPPER_RED = np.array([5, 255, 255])     
LOWER_ORANGE = np.array([5, 100, 150])
UPPER_ORANGE = np.array([88, 255, 255]) 
LOWER_GREEN = np.array([69, 63, 97])
UPPER_GREEN = np.array([135, 255, 255])  

cap = cv2.VideoCapture(0)
detector = cv2.QRCodeDetector()

while True:
    success, img = cap.read()
    img = imutils.resize(img, width=400)
    
    data, bbox = scan()
    
    if data != "":
        rect = transform()
        img_hsv = cv2.cvtColor(rect, cv2.COLOR_BGR2HSV)
        classify()
    
    cv2.imshow("Health Code Detection", img)
    
    if cv2.waitKey(100) == ord("q"):
        exit()