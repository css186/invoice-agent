from PIL import Image
import numpy as np
import io
import base64

def is_blank_image(image_bytes: bytes, threshold: float = 245.0) -> bool:
    """
    Check if the image is blank (white) or not.
    """
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("L")
        image_array = np.array(image)
        return image_array.mean() > threshold
    except Exception as e:
        return False


def is_mostly_black_image(image_bytes: bytes, threshold: float = 0.99) -> bool:
    """
    Return True if the image is mostly black (pixel values near 0).
    """
    image = Image.open(io.BytesIO(image_bytes)).convert("L") 
    arr = np.asarray(image) / 255.0  

    black_ratio = np.mean(arr < 0.02)
    return black_ratio > threshold

def is_mostly_black_pdf_from_pages(pages: list, threshold: float = 0.99) -> bool:
    """
    Return True if ALL pages are mostly black.
    """
    for page in pages:
        base64_data = page.get("data")
        if not base64_data:
            continue
        try:
            image_bytes = base64.b64decode(base64_data)
            if not is_mostly_black_image(image_bytes, threshold):
                return False 
        except Exception:
            continue
    return True