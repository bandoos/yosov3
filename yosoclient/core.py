"""
Core module defining the API wrapper client.
Can be used programmatically from python, or exposed as cli (see yosoclient.cli)
"""
import os
import io
import cv2
import requests
import numpy as np
from yosoclient.config import ClientConfig
from yosoclient.console import console
import json


def with_confidence(url: str, confidence: float):
    "Add confidence param to the url"
    return url + f"&confidence={confidence}"


def img_from_response(response: requests.Response):
    "Decode image as cv2 image from an http response"
    image_stream = io.BytesIO(response.content)
    image_stream.seek(0)
    file_bytes = np.asarray(bytearray(image_stream.read()), dtype=np.uint8)
    return cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)


class Client:
    """Client wrapper for the prediction API"""

    def __init__(self, conf: ClientConfig):
        self.conf = conf

    def mk_url(self, endpoint: str):
        "Produce the url string for some endpoint"
        return f"http://{self.conf.host}:{self.conf.port}/{endpoint}?model={self.conf.model}"

    def request_error(self, url: str, code: int):
        raise Exception(
            f"The reqest to {url} was not successfull. CODE={code}")

    def response_from_server(self,
                             url: str,
                             image_file,
                             verbose=True,
                             confidence=0.5):
        """Main entry point to make a request to the prediction server.
        Should not be used directly. Returns raw requests.Response object
        """
        files = {'file': image_file}
        url_with_confidence = with_confidence(url, confidence)
        console.log(
            f"[yellow]Request to prediction server at url: {url_with_confidence}[/]"
        )
        resp = requests.post(url_with_confidence, files=files)
        status_code = resp.status_code
        if verbose:
            msg = "Everything went well!" if status_code == 200 else "There was an error when handling the request."
            console.log(msg)
        return resp

    def save_img_from_response(self,
                               response: requests.Response,
                               filename="latest_response.jpeg",
                               dest_dir=None):
        """Decode image from response and save under `filename` within `dest_dir`
        """
        image = img_from_response(response)
        dest_dir = self.conf.response_image_dir if dest_dir is None else dest_dir
        dest = os.path.join(dest_dir, filename)
        console.log(f"Saving image response to {dest}")
        cv2.imwrite(dest, image)

    def predict_request(self, image_path: str, confidence=0.5, dest_dir=None):
        """
        Make a /predict request to the server and save the image response to
        the configured `response_image_dir` under the same base name as `image_path`
        """
        url = self.mk_url("predict")
        base_name = os.path.basename(image_path)
        with open(image_path, "rb") as image_file:
            resp = self.response_from_server(
                url,
                image_file,
                confidence=confidence,
            )
            if resp.status_code == 200:
                self.save_img_from_response(resp,
                                            filename=base_name,
                                            dest_dir=dest_dir)
            else:
                self.request_error(resp.url, resp.status_code)

    def count_objects_request(self, image_path: str, confidence=0.5):
        """
        Make a /count_objects request to the server and return the json decoded response.
        """
        url = self.mk_url("count_objects")
        with open(image_path, "rb") as image_file:
            resp = self.response_from_server(url,
                                             image_file,
                                             confidence=confidence)
            if resp.status_code == 200:
                return resp.json()
            else:
                self.request_error(resp.url, resp.status_code)


# if __name__ == "__main__":
#     config = ClientConfig()
#     client = Client(config)

#     client.predict_request(
#         "/home/bandoos/MLOPS/labs/machine-learning-engineering-for-production-public/course1/week1-ungraded-lab/images/car.jpg"
#     )
