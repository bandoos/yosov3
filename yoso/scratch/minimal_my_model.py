from enum import Enum
import os
import io
import numpy as np
import cv2
import cvlib as cv
#from cvlib.object_detection import draw_bbox
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
import uvicorn
from yoso.model.my_model import DetectionModel

app = FastAPI(title="minimal server")
host = "localhost"
port = 8042
upload_dir = "/tmp/minimal_upload_dir"

if not os.path.exists(upload_dir):
    os.mkdir(upload_dir)

welcome_page = f"""
Congratulations! Your API is working as expected.<br/>
Now head over to <a href='http://{host}:{port}/docs'> docs </a>.
"""


def validate_image_file(file: UploadFile, exts={"jpg", "jpeg", "png"}):
    """Validate the extension of the some uploaded file."""
    filename = file.filename
    fileExtension = filename.split(".")[-1] in exts
    if not fileExtension:
        raise HTTPException(status_code=415,
                            detail="Unsupported file provided.")


def file_to_cv_image(file: UploadFile):
    """Convert raw image file to cv2 image"""

    image_stream = io.BytesIO(
        file.file.read())  # Read image as a stream of bytes
    image_stream.seek(0)
    # Write the stream of bytes into a numpy array
    file_bytes = np.asarray(bytearray(image_stream.read()), dtype=np.uint8)
    # Decode the numpy array as an image

    return cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)


# Model selection enum
class Model(str, Enum):
    yolov3tiny = "yolov3-tiny"
    yolov3 = "yolov3"


## Define routes
@app.get("/")
def home():
    return HTMLResponse(content=welcome_page, status_code=200)


od_model = DetectionModel()


# This endpoint handles all the logic necessary for the object detection to work.
# It requires the desired model and the image in which to perform object detection.
@app.post("/predict", summary="Perform object detection.")
def prediction(model: Model,
               confidence: float = 0.5,
               file: UploadFile = File(...)):
    validate_image_file(file)
    image = file_to_cv_image(file)

    #od_model = DetectionModel()

    bbox, label, conf = od_model.detect_common_objects(
        image,
        model=model,
        # extra, pass the confidence level
        confidence=confidence)

    # Create image that includes bounding boxes and labels
    output_image = od_model.draw_bbox(image,
                                      bbox,
                                      label,
                                      conf,
                                      write_conf=True)

    img_path = os.path.join(upload_dir, file.filename)
    # Save it in a folder within the server
    cv2.imwrite(img_path, output_image)

    # 4. STREAM THE RESPONSE BACK TO THE CLIENT

    # Open the saved image for reading in binary mode
    file_image = open(img_path, mode="rb")

    # Return the image as a stream specifying media type
    return StreamingResponse(file_image, media_type="image/jpeg")


if __name__ == "__main__":
    uvicorn.run(app, host=host, port=port)
