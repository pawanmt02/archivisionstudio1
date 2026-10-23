import cv2
import numpy as np
import base64
from PIL import Image
import io

def base64_to_numpy(b64_string: str) -> np.ndarray:
    """Decode base64 PNG/JPEG to numpy BGR array"""
    if "," in b64_string:
        b64_string = b64_string.split(",")[1]
    
    image_data = base64.b64decode(b64_string)
    image = Image.open(io.BytesIO(image_data))
    
    if image.mode == 'RGBA':
        # Create a white background
        background = Image.new('RGB', image.size, (255, 255, 255))
        background.paste(image, mask=image.split()[3])
        image = background
    elif image.mode != 'RGB':
        image = image.convert('RGB')
        
    np_img = np.array(image)
    return cv2.cvtColor(np_img, cv2.COLOR_RGB2BGR)

def numpy_to_base64(img: np.ndarray, format='PNG') -> str:
    """Encode numpy BGR array to base64 PNG string"""
    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(rgb_img)
    buffered = io.BytesIO()
    pil_img.save(buffered, format=format)
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{img_str}"

def preprocess_sketch(b64_sketch: str) -> tuple[np.ndarray, str]:
    """
    Full CV preprocessing pipeline for MAXIMUM sketch accuracy:
    1. Decode base64 to numpy BGR
    2. Resize to exactly 512x512
    3. Convert to grayscale
    4. Strict Thresholding (captures every single drawn line, even faint ones)
    5. Minimal dilation to solidify lines for ControlNet without losing detail
    6. Convert back to BGR 3-channel for compatibility
    Returns: (processed_numpy_array_BGR, base64_string_of_processed_image)
    """
    img = base64_to_numpy(b64_sketch)
    
    # 2. Resize to 512x512
    img_resized = cv2.resize(img, (512, 512), interpolation=cv2.INTER_AREA)
    
    # 3. Convert to grayscale
    gray = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)
    
    # 4. Strict sensitivity threshold:
    # Our canvas is pure white (255). We want to catch ANY pixel that was drawn on (anything < 250).
    # THRESH_BINARY_INV turns the white background black (0) and the drawn lines white (255)
    _, inverted = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY_INV)
    
    # 5. Minimal dilation: just enough to ensure the AI detects the line, but thin enough to keep exact detail.
    kernel = np.ones((2, 2), np.uint8)
    dilated = cv2.dilate(inverted, kernel, iterations=1)
    
    # 5.5 ARCHITECTURAL VALIDATION (Forgiving Hough Transform)
    # Hand-drawn sketches on a web canvas are naturally wavy and jagged.
    # We use a forgiving Hough Transform to verify there is SOME geometric intent (walls, roofs).
    # If the user draws at least 3 somewhat straight lines, we accept it as architecture.
    lines = cv2.HoughLinesP(dilated, 1, np.pi / 180, threshold=25, minLineLength=25, maxLineGap=15)
    
    if lines is None or len(lines) < 3:
        raise ValueError("Non-Architectural Sketch Detected: Architecture requires geometric intent. Please ensure your drawing has distinct straight lines (e.g., walls, floors, or a roof).")

        
    # 6. Convert back to BGR 3-channel
    final_bgr = cv2.cvtColor(dilated, cv2.COLOR_GRAY2BGR)
    
    b64_out = numpy_to_base64(final_bgr)
    return final_bgr, b64_out
