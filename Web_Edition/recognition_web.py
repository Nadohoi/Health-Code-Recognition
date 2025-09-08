from flask import Flask, Response, render_template
from imutils.video import WebcamVideoStream
from imutils.perspective import four_point_transform
import cv2
import numpy as np
import winsound
from time import sleep
import threading
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)

# --- Your color ranges (kept as in your original code) ---
LOWER_RED = np.array([3, 60, 60])
UPPER_RED = np.array([5, 255, 255])
LOWER_ORANGE = np.array([5, 100, 150])
UPPER_ORANGE = np.array([88, 255, 255])
LOWER_GREEN = np.array([69, 63, 97])
UPPER_GREEN = np.array([135, 255, 255])

# --- Camera and detector ---
cap = WebcamVideoStream(src=0).start()
detector = cv2.QRCodeDetector()

frame_lock = threading.Lock()
output_frame = None  # the latest processed frame (BGR)

# Helper: play beep in background so it doesn't block frame processing
def beep_async(freq, duration_ms):
    def _b():
        try:
            winsound.Beep(freq, duration_ms)
        except Exception:
            pass
    t = threading.Thread(target=_b, daemon=True)
    t.start()

# Keep core functions similar to your script but adapted for thread usage
def annotate_image_with_text(image, status):
    """
    Annotate the image with status text in Chinese
    
    Args:
        image: Input image in BGR format
        status: Either 'GO' or 'STOP'
    Returns:
        Annotated image in BGR format
    """
    # Convert the image to PIL format
    img_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    
    # Try to use Microsoft YaHei font, fallback to default if not available
    try:
        font = ImageFont.truetype("msyh.ttc", 100)  # Microsoft YaHei font
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
    
    # Play beep asynchronously
    beep_async(beep_freq, beep_duration)
    
    # Convert back to OpenCV format
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

def classify_and_annotate(img, img_hsv):
    """
    Classify the health code color and annotate the image.
    Returns annotated img.
    """
    mask_red = cv2.inRange(img_hsv, LOWER_RED, UPPER_RED)
    mask_orange = cv2.inRange(img_hsv, LOWER_ORANGE, UPPER_ORANGE)
    mask_green = cv2.inRange(img_hsv, LOWER_GREEN, UPPER_GREEN)

    red_pixels = np.count_nonzero(mask_red)
    orange_pixels = np.count_nonzero(mask_orange)
    green_pixels = np.count_nonzero(mask_green)

    if green_pixels > red_pixels and green_pixels > orange_pixels:
        return annotate_image_with_text(img, "GO")
    else:
        return annotate_image_with_text(img, "STOP")

def safe_scan_and_transform(img):
    """
    Try to detect and decode QR code.
    Returns (transformed_rect, data) if successful, (None, None) otherwise.
    """
    try:
        data, bbox, _ = detector.detectAndDecode(img)
        if not data or bbox is None:
            return None, None
            
        # Convert bbox to correct format
        bbox = np.int32(bbox).reshape(4, 2)
        rect = four_point_transform(img, bbox)
        return rect, data
    except Exception as e:
        print(f"Error in QR processing: {e}")
        return None, None

def processing_loop():
    """Background thread reading frames, processing them, and storing latest annotated frame."""
    global output_frame
    while True:
        frame = cap.read()
        if frame is None:
            continue
            
        # Make a copy of the frame for display
        display_frame = frame.copy()
        
        # Try to detect and process QR code
        rect, data = safe_scan_and_transform(frame)
        if rect is not None and data:
            # Convert ROI to HSV and classify
            img_hsv = cv2.cvtColor(rect, cv2.COLOR_BGR2HSV)
            display_frame = classify_and_annotate(frame, img_hsv)
            
        # Store the latest processed frame for the web stream
        with frame_lock:
            output_frame = display_frame.copy()

# Start background processing thread once
proc_thread = threading.Thread(target=processing_loop, daemon=True)
proc_thread.start()

def gen_frames():
    """Generator for MJPEG streaming of the processed frames."""
    global output_frame
    while True:
        with frame_lock:
            if output_frame is None:
                # If we don't have a processed frame yet, just wait a little and continue
                frame = None
            else:
                frame = output_frame.copy()

        if frame is None:
            # small sleep to avoid busy loop
            sleep(0.01)
            continue

        # Encode frame as JPEG
        ret, jpeg = cv2.imencode('.jpg', frame)
        if not ret:
            continue

        frame_bytes = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    try:
        # Use threaded=True to allow multiple clients; change host/port as needed
        app.run(host='0.0.0.0', port=5000, threaded=True)
    finally:
        try:
            cap.stop()
        except Exception:
            pass