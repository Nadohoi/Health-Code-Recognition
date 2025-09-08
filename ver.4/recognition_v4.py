# Import the necessary packages
from imutils.perspective import four_point_transform
from imutils.video import WebcamVideoStream
import cv2
import numpy as np
from winsound import Beep
from PIL import Image, ImageDraw, ImageFont

def annotate_image(image, status, display_duration=2000):
    # Convert the image to PIL format
    img_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    
    # Try to use a nice font, fallback to default if not available
    try:
        font = ImageFont.truetype("msyh.ttc", 100)  # Bold Arial, size 100
    except:
        font = ImageFont.load_default()
    
    if status.upper() == 'GO':
        text = "通行"
        text_color = (0, 200, 0)  # Bright green
        shadow_color = (0, 100, 0)  # Dark green shadow
        beep_freq = 1250
        beep_duration = 200
    else:  # STOP
        text = "禁止通行"
        text_color = (255, 50, 50)  # Bright red
        shadow_color = (150, 0, 0)  # Dark red shadow
        beep_freq = 500
        beep_duration = 3000
    
    # Get text bounding box and calculate position
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    text_width = right - left
    text_height = bottom - top
    x = (image.shape[1] - text_width) // 2  # Center horizontally
    y = image.shape[0] // 3  # Position from top
    
    # Draw shadow (slightly offset)
    draw.text((x+3, y+3), text, font=font, fill=shadow_color)
    # Draw main text
    draw.text((x, y), text, font=font, fill=text_color)
    
    # Convert back to OpenCV format
    img_with_text = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
    
    # Show the result
    cv2.imshow("Health Code Detection", img_with_text)
    Beep(beep_freq, beep_duration)
    cv2.waitKey(display_duration)

def classify():
    # returns a 2D array, where each pixel is either 0 or 255 (255 means the pixel is in the range)
    mask_red = cv2.inRange(img_hsv, LOWER_RED, UPPER_RED)
    mask_orange = cv2.inRange(img_hsv, LOWER_ORANGE, UPPER_ORANGE)
    mask_green = cv2.inRange(img_hsv, LOWER_GREEN, UPPER_GREEN)

    red_pixels = np.count_nonzero(mask_red)
    orange_pixels = np.count_nonzero(mask_orange)
    green_pixels = np.count_nonzero(mask_green)
    
    if green_pixels > red_pixels and green_pixels > orange_pixels:
        status = "GO"
    else:
        status = "STOP"
    
    # Annotate and display the image
    annotate_image(img.copy(), status)

def scan():
    data, bbox, _ = detector.detectAndDecode(img)
    return data, bbox

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

cap = WebcamVideoStream(src = 0).start()
detector = cv2.QRCodeDetector()

while True:
    img = cap.read()

    data, bbox = scan()
    
    if data != "":
        rect = transform()
        img_hsv = cv2.cvtColor(rect, cv2.COLOR_BGR2HSV)
        classify()
    
    cv2.imshow("Health Code Detection", img)
    
    if cv2.waitKey(150) == ord("q"):
        exit()