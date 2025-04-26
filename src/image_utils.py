import io
import base64
from PIL import Image
from .config import MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT, MAX_IMAGE_SIZE_MB

def compress_image(image):
    # Compress image if it exceeds size limits.
    img_format = image.format or "PNG"
    img_io = io.BytesIO()

    # Resize if too large
    if image.width > MAX_IMAGE_WIDTH or image.height > MAX_IMAGE_HEIGHT:
        image.thumbnail((MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT))

    # Save compressed image
    image.save(img_io, format=img_format, quality=85)
    img_io.seek(0)

    return img_io

def encode_image(image):
    # Encodes the image as base64.
    img_io = io.BytesIO()
    image.save(img_io, format="PNG")  # Convert to PNG for base64 encoding
    img_io.seek(0)
    return base64.b64encode(img_io.read()).decode("utf-8")

def validate_image_size(image_file):
    # Check if the image exceeds the maximum size in MB.
    image_file.seek(0, io.SEEK_END)
    file_size_mb = image_file.tell() / (1024 * 1024)  # Convert bytes to MB
    image_file.seek(0)
    return file_size_mb
