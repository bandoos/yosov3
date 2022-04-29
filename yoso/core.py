"""
Core module of this project.

Exposes the basic pretrained yolo models from `cvlib`
via `cvlib.detect_common_objects` as a fastapi server.
This showcases a basic prediction server setup.

A request on the `/predict` endpoint passing the dired model name,
an optional confidence level, and an image file to process, will
produce a response being the image with delimiting boxes drawn,
and label indication (with confidence level annotation).

A request on the `/count_objects` endpoint will return a {items: Dict [str,int]}
structure with the counts of objects per label

This software is adapted from coursera `introduction-to-machine-learning-in-production`
ungraded lab week 1.

"""
import os
from collections import Counter
import cv2
import cvlib as cv
from cvlib.object_detection import draw_bbox
# import nest_asyncio # for usage in jupyter
from enum import Enum
from pprint import pprint

## Fastapi imports
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.responses import StreamingResponse, HTMLResponse, JSONResponse
## Tracing
from opentelemetry import trace

## Internal package imports
from yoso.console import console
import yoso.utils as utils
from yoso.cvutils import file_to_cv_image
from yoso.config import ServerConfig
# Api models
from yoso.api_models import CounterResponse


# Model selection enum
class Model(str, Enum):
    yolov3tiny = "yolov3-tiny"
    yolov3 = "yolov3"


# Load configuration

console.log("Loading configuration...")
config = ServerConfig()
pprint(config.dict())

# instatiate fastapi app
app = FastAPI(title=config.title)

welcome_page = f"""
Congratulations! Your API is working as expected.<br/>
Now head over to <a href='http://{config.host}:{config.port}/docs'> docs </a>.
"""


class TracingDeps:
    "Injectable dependency for fine-grained tracing"

    def __init__(self):
        self.tracer = trace.get_tracer(config.service_name)


## Define routes
@app.get("/")
def home():
    return HTMLResponse(content=welcome_page, status_code=200)


# This endpoint handles all the logic necessary for the object detection to work.
# It requires the desired model and the image in which to perform object detection.
@app.post("/predict", summary="Perform object detection.")
def prediction(model: Model,
               confidence: float = 0.5,
               file: UploadFile = File(...),
               tracing: TracingDeps = Depends(TracingDeps)):

    # 1. VALIDATE INPUT FILE
    utils.validate_image_file(file)

    # 2. TRANSFORM RAW IMAGE INTO CV2 image
    image = file_to_cv_image(file)

    # 3. RUN OBJECT DETECTION MODEL

    with tracing.tracer.start_as_current_span("cv-model"):
        bbox, label, conf = cv.detect_common_objects(
            image,
            model=model,
            # extra, pass the confidence level
            confidence=confidence)

    # Create image that includes bounding boxes and labels
    output_image = draw_bbox(image, bbox, label, conf, write_conf=True)

    img_path = os.path.join(config.upload_dir, file.filename)
    # Save it in a folder within the server
    cv2.imwrite(img_path, output_image)

    # 4. STREAM THE RESPONSE BACK TO THE CLIENT

    # Open the saved image for reading in binary mode
    file_image = open(img_path, mode="rb")

    # Return the image as a stream specifying media type
    return StreamingResponse(file_image, media_type="image/jpeg")


@app.post("/count_objects", response_model=CounterResponse)
def count_objects(model: Model,
                  confidence: float = 0.5,
                  file: UploadFile = File(...),
                  tracing: TracingDeps = Depends(TracingDeps)):
    # 1. VALIDATE INPUT FILE
    utils.validate_image_file(file)

    # 2. TRANSFORM RAW IMAGE INTO CV2 image
    image = file_to_cv_image(file)

    with tracing.tracer.start_as_current_span("cv-model"):
        # 3. RUN OBJECT DETECTION MODEL
        _, label, _ = cv.detect_common_objects(
            image,
            model=model,
            # extra, pass the confidence level
            confidence=confidence)

    c = Counter(label)

    return CounterResponse(items=dict(c))
