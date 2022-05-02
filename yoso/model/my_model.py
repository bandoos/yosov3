import cv2
import os
import numpy as np
from cvlib.utils import download_file
import threading
from functools import wraps


def locking(method):

    @wraps(method)
    def inner(ref, *args, **kwargs):
        ref.lock.acquire()
        ret = method(ref, *args, **kwargs)
        ref.lock.release()
        return ret

    return inner


class DetectionModel:

    def __init__(self):
        self.initialize = True
        self.net = None
        self.dest_dir = os.path.expanduser(
            '~'
        ) + os.path.sep + '.cvlib' + os.path.sep + 'object_detection' + os.path.sep + 'yolo' + os.path.sep + 'yolov3'
        self.classes = None
        self.COLORS = np.random.uniform(0, 255, size=(80, 3))
        self.lock = threading.Lock()

    def populate_class_labels(self):

        class_file_name = 'yolov3_classes.txt'
        class_file_abs_path = self.dest_dir + os.path.sep + class_file_name
        url = 'https://github.com/arunponnusamy/object-detection-opencv/raw/master/yolov3.txt'
        if not os.path.exists(class_file_abs_path):
            download_file(url=url,
                          file_name=class_file_name,
                          dest_dir=self.dest_dir)
        f = open(class_file_abs_path, 'r')
        self.classes = [line.strip() for line in f.readlines()]

        return self.classes

    def get_output_layers(self):
        layer_names = self.net.getLayerNames()
        #print(layer_names)

        #print(self.net.getUnconnectedOutLayers())
        output_layers = [
            layer_names[i[0] - 1] for i in self.net.getUnconnectedOutLayers()
        ]

        return output_layers

    def draw_bbox(self,
                  img,
                  bbox,
                  labels,
                  confidence,
                  colors=None,
                  write_conf=False):
        """A method to apply a box to the image
        Args:
            img: An image in the form of a numPy array
            bbox: An array of bounding boxes
            labels: An array of labels
            colors: An array of colours the length of the number of targets(80)
            write_conf: An option to write the confidences to the image
        """

        COLORS = self.COLORS
        classes = self.classes

        if classes is None:
            classes = self.populate_class_labels()

        for i, label in enumerate(labels):

            if colors is None:
                color = COLORS[classes.index(label)]
            else:
                color = colors[classes.index(label)]

            if write_conf:
                label += ' ' + str(format(confidence[i] * 100, '.2f')) + '%'

            cv2.rectangle(img, (bbox[i][0], bbox[i][1]),
                          (bbox[i][2], bbox[i][3]), color, 2)

            cv2.putText(img, label, (bbox[i][0], bbox[i][1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        return img

    @locking
    def detect_common_objects(self,
                              image,
                              confidence=0.5,
                              nms_thresh=0.3,
                              model='yolov4',
                              enable_gpu=False):
        """A method to detect common objects
        Args:
            image: A colour image in a numpy array
            confidence: A value to filter out objects recognised to a lower confidence score
            nms_thresh: An NMS value
            model: The detection model to be used, supported models are: yolov3, yolov3-tiny, yolov4, yolov4-tiny
            enable_gpu: A boolean to set whether the GPU will be used
        """

        Height, Width = image.shape[:2]
        scale = 0.00392

        classes = self.classes
        dest_dir = self.dest_dir

        if model == 'yolov3-tiny':
            config_file_name = 'yolov3-tiny.cfg'
            cfg_url = "https://github.com/pjreddie/darknet/raw/master/cfg/yolov3-tiny.cfg"
            weights_file_name = 'yolov3-tiny.weights'
            weights_url = 'https://pjreddie.com/media/files/yolov3-tiny.weights'
            blob = cv2.dnn.blobFromImage(image,
                                         scale, (416, 416), (0, 0, 0),
                                         True,
                                         crop=False)

        elif model == 'yolov4':
            config_file_name = 'yolov4.cfg'
            cfg_url = 'https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/yolov4.cfg'
            weights_file_name = 'yolov4.weights'
            weights_url = 'https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v3_optimal/yolov4.weights'
            blob = cv2.dnn.blobFromImage(image,
                                         scale, (416, 416), (0, 0, 0),
                                         True,
                                         crop=False)

        elif model == 'yolov4-tiny':
            config_file_name = 'yolov4-tiny.cfg'
            cfg_url = 'https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/yolov4-tiny.cfg'
            weights_file_name = 'yolov4-tiny.weights'
            weights_url = 'https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v4_pre/yolov4-tiny.weights'
            blob = cv2.dnn.blobFromImage(image,
                                         scale, (416, 416), (0, 0, 0),
                                         True,
                                         crop=False)

        else:
            config_file_name = 'yolov3.cfg'
            cfg_url = 'https://github.com/arunponnusamy/object-detection-opencv/raw/master/yolov3.cfg'
            weights_file_name = 'yolov3.weights'
            weights_url = 'https://pjreddie.com/media/files/yolov3.weights'
            blob = cv2.dnn.blobFromImage(image,
                                         scale, (416, 416), (0, 0, 0),
                                         True,
                                         crop=False)

        config_file_abs_path = dest_dir + os.path.sep + config_file_name
        weights_file_abs_path = dest_dir + os.path.sep + weights_file_name

        if not os.path.exists(config_file_abs_path):
            download_file(url=cfg_url,
                          file_name=config_file_name,
                          dest_dir=dest_dir)

        if not os.path.exists(weights_file_abs_path):
            download_file(url=weights_url,
                          file_name=weights_file_name,
                          dest_dir=dest_dir)

        if self.initialize:
            classes = self.populate_class_labels()
            self.net = cv2.dnn.readNet(weights_file_abs_path,
                                       config_file_abs_path)
            self.initialize = False

        # enables opencv dnn module to use CUDA on Nvidia card instead of cpu
        if enable_gpu:
            self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
            self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

        self.net.setInput(blob)

        outs = self.net.forward(self.get_output_layers())

        class_ids = []
        confidences = []
        boxes = []

        for out in outs:
            for detection in out:
                try:
                    scores = detection[5:]
                    class_id = np.argmax(scores)
                    max_conf = scores[class_id]
                    if max_conf > confidence:
                        center_x = int(detection[0] * Width)
                        center_y = int(detection[1] * Height)
                        w = int(detection[2] * Width)
                        h = int(detection[3] * Height)
                        x = center_x - (w / 2)
                        y = center_y - (h / 2)
                        class_ids.append(class_id)
                        confidences.append(float(max_conf))
                        boxes.append([x, y, w, h])
                except Exception as e:
                    print("---->", outs)
                    raise (e)

        indices = cv2.dnn.NMSBoxes(boxes, confidences, confidence, nms_thresh)

        bbox = []
        label = []
        conf = []

        for idx in indices:
            i = idx[0]
            box = boxes[i]
            x = box[0]
            y = box[1]
            w = box[2]
            h = box[3]
            bbox.append([int(x), int(y), int(x + w), int(y + h)])
            label.append(str(classes[class_ids[i]]))
            conf.append(confidences[i])

        return bbox, label, conf
