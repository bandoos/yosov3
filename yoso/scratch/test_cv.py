import io
import numpy as np
import cv2
import cvlib as cv
from multiprocessing import Pool


def predict_labels(file_path, model="yolov3-tiny", confidence=0.5):
    with open(file_path, 'rb') as file:
        image_stream = io.BytesIO(
            file.read())  # Read image as a stream of bytes
        image_stream.seek(0)
        # Write the stream of bytes into a numpy array
        file_bytes = np.asarray(bytearray(image_stream.read()), dtype=np.uint8)
        # Decode the numpy array as an image

        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        bbox, label, conf = cv.detect_common_objects(
            img,
            model=model,
            # extra, pass the confidence level
            confidence=confidence)

        print(label)
        return label


def sequential_stress():
    path = "/home/bandoos/repos/YOSOv3/images/apple.jpg"
    for i in range(1000):
        print(predict_labels(path))


def multiprocessing_stress(n_procs=4):
    path = "/home/bandoos/repos/YOSOv3/images/apple.jpg"
    with Pool(processes=n_procs) as p:
        p.map(predict_labels, [path] * (n_procs * 100))


if __name__ == "__main__":
    #sequential_stress()
    multiprocessing_stress(n_procs=10)
