import base64
import random
import string
import uuid
from functools import lru_cache

import cv2
import numpy as np
from fastapi import APIRouter

from schemas.captcha import CaptchaResponse

router = APIRouter()

@lru_cache(maxsize=1024)
def get_captcha_store():
    return {}

def generate_captcha_harder():
    """
    Generates a more complex and harder-to-solve distorted text image for CAPTCHA.
    """
    width, height = 240, 80
    
    background = np.zeros((height, width, 3), dtype=np.uint8)
    for y in range(height):
        color_val = 230 + int(25 * (y / height)) # Gradient from 230 to 255
        background[y, :] = [color_val, color_val, color_val]

    captcha_text = ''.join(random.choices(string.ascii_letters + string.digits, k=6))

    image = background.copy()
    font = cv2.FONT_HERSHEY_SIMPLEX
    x_offset = 15  # Starting padding

    for char in captcha_text:
        # Per-character variations
        font_scale = random.uniform(1.1, 1.4)
        font_thickness = random.randint(2, 3)
        char_color = (random.randint(0, 120), random.randint(0, 120), random.randint(0, 120))
        
        # Get character size to calculate placement
        (text_width, text_height), baseline = cv2.getTextSize(char, font, font_scale, font_thickness)
        
        # Random vertical offset
        y_offset = (height + text_height) // 2 + random.randint(-8, 8)
        
        cv2.putText(image, char, (x_offset, y_offset), font, font_scale, char_color, font_thickness, cv2.LINE_AA)
        
        # Update x_offset for the next character
        x_offset += text_width + random.randint(-5, 5) # Variable spacing

    # Add noise lines
    for _ in range(8):
        pt1 = (random.randint(0, width), random.randint(0, height))
        pt2 = (random.randint(0, width), random.randint(0, height))
        line_color = (random.randint(100, 200), random.randint(100, 200), random.randint(100, 200))
        cv2.line(image, pt1, pt2, line_color, 1)

    # Add "salt and pepper" noise
    noise_level = 0.03 # 3% of pixels will be noise
    num_noise_pixels = int(width * height * noise_level)
    for _ in range(num_noise_pixels):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        noise_color = random.choice([(0, 0, 0), (255, 255, 255)]) # Black or white
        image[y, x] = noise_color

    distorted_image = image.copy()
    rows, cols, _ = distorted_image.shape
    
    # Create a mapping for distortion
    map_x = np.zeros((rows, cols), dtype=np.float32)
    map_y = np.zeros((rows, cols), dtype=np.float32)

    for y in range(rows):
        for x in range(cols):
            # Composite wave: combination of two sine waves for a less regular pattern
            offset_x = int(12.0 * np.sin(2 * 3.14 * y / 150) + 8.0 * np.sin(2 * 3.14 * y / 60))
            offset_y = int(8.0 * np.sin(2 * 3.14 * x / 180))
            
            map_x[y, x] = float(x + offset_x)
            map_y[y, x] = float(y + offset_y)
    
    cv2.remap(image, map_x, map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE, dst=distorted_image)

    # Encode final image to base64
    _, buffer = cv2.imencode('.png', distorted_image)
    image_base64 = base64.b64encode(buffer).decode('utf-8')

    return captcha_text, image_base64

@router.get("/", response_model=CaptchaResponse)
def get_new_captcha():
    """
    Generate a new CAPTCHA, store its value, and return the image.
    """
    captcha_store = get_captcha_store()
    captcha_id = str(uuid.uuid4())
    
    text, image_b64 = generate_captcha_harder()
    
    captcha_store[captcha_id] = text
    
    return CaptchaResponse(captcha_id=captcha_id, image_base64=image_b64)