import io
import numpy as np
import cv2
import cvlib as cv
from fastapi import UploadFile


def file_to_cv_image(file: UploadFile):
    """Convert raw image file to cv2 image"""

    image_stream = io.BytesIO(
        file.file.read())  # Read image as a stream of bytes
    image_stream.seek(0)
    # Write the stream of bytes into a numpy array
    file_bytes = np.asarray(bytearray(image_stream.read()), dtype=np.uint8)
    # Decode the numpy array as an image

    return cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
