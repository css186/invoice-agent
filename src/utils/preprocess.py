from PIL import Image, ImageFilter, ImageOps
import io

def preprocess_file(file_bytes: bytes) -> bytes:

    img = Image.open(io.BytesIO(file_bytes)).convert("L")

    img = img.point(lambda p: 0 if p < 128 else 255)

    img = img.filter(ImageFilter.MedianFilter(size=3))

    img = ImageOps.autocontrast(img)

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")

    return buffer.getvalue()