# python3
#
# Copyright 2019 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Example using TF Lite to detect objects with the Raspberry Pi camera."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import io
import re
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from multiprocessing import Process, Pipe, Queue

from annotation import Annotator

import numpy as np
import picamera

from PIL import Image
from tflite_runtime.interpreter import Interpreter

CAMERA_WIDTH = 512
CAMERA_HEIGHT = 512


def load_labels(path):
    """Loads the labels file. Supports files with or without index numbers."""
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        labels = {}
        for row_number, content in enumerate(lines):
            pair = re.split(r'[:\s]+', content.strip(), maxsplit=1)
            if len(pair) == 2 and pair[0].strip().isdigit():
                labels[int(pair[0])] = pair[1].strip()
            else:
                labels[row_number] = pair[0].strip()
    return labels


def set_input_tensor(interpreter, image):
    """Sets the input tensor."""
    input_tensor = np.expand_dims(image, 0)


def get_output_tensor(interpreter, index):
    """Returns the output tensor at the given index."""
    output_details = interpreter.get_output_details()[index]
    tensor = np.squeeze(interpreter.get_tensor(output_details['index']))
    return tensor


def detect_objects(interpreter, image, threshold):
    """Returns a list of detection results, each a dictionary of object info."""
    input_tensor = np.expand_dims(image, 0)
    interpreter.invoke()

    # Get all output details
    boxes = get_output_tensor(interpreter, 0)
    classes = get_output_tensor(interpreter, 1)
    scores = get_output_tensor(interpreter, 2)
    count = int(get_output_tensor(interpreter, 3))

    results = []
    for i in range(count):
        if scores[i] >= threshold:
            result = {
                'bounding_box': boxes[i],
                'class_id': classes[i],
                'score': scores[i]
            }
            results.append(result)
    return results


def annotate_objects(annotator, results, labels):
    """Draws the bounding box and label for each object in the results."""
    for obj in results:
        # Convert the bounding box figures from relative coordinates
        # to absolute coordinates based on the original resolution
        ymin, xmin, ymax, xmax = obj['bounding_box']
        xmin = int(xmin * CAMERA_WIDTH)
        xmax = int(xmax * CAMERA_WIDTH)
        ymin = int(ymin * CAMERA_HEIGHT)
        ymax = int(ymax * CAMERA_HEIGHT)

        # Overlay the box, label, and score on the camera preview
        annotator.bounding_box([xmin, ymin, xmax, ymax])
        annotator.text([xmin, ymin],
                       '%s\n%.2f' % (labels[obj['class_id']], obj['score']))


def load_image_into_numpy_array(data: io.BytesIO):
    """Load an image from file into a numpy array.

    Puts image into numpy array to feed into tensorflow graph.
    Note that by convention we put it into a numpy array with shape
    (height, width, channels), where channels=3 for RGB.

    Args:
      path: a file path (this can be local or on colossus)

    Returns:
      uint8 numpy array with shape (img_height, img_width, 3)
    """
    image = Image.open(data)
    (im_width, im_height) = image.size
    return np.array(image.getdata()).reshape(
        (im_height, im_width, 3)).astype(np.uint8)


def run_tensorflow_inference(queue: Queue):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '--model', help='File path of .tflite file.', required=True)
    parser.add_argument(
        '--labels', help='File path of labels file.', required=True)
    parser.add_argument(
        '--threshold',
        help='Score threshold for detected objects.',
        required=False,
        type=float,
        default=0.4)
    args = parser.parse_args()

    labels = load_labels(args.labels)
    interpreter = Interpreter(args.model)
    interpreter.allocate_tensors()

    _, input_height, input_width, _ = interpreter.get_input_details()[
        0]['shape']

    with picamera.PiCamera(
            resolution=(CAMERA_WIDTH, CAMERA_HEIGHT), framerate=30) as camera:
        camera.start_preview()
        try:
            stream = io.BytesIO()
            annotator = Annotator(camera)

            for _ in camera.capture_continuous(
                    stream, format='jpeg', use_video_port=True):
                stream.seek(0)
                # image = Image.open(stream).convert('RGB').resize(
                #   (input_width, input_height), Image.ANTIALIAS)
                image = load_image_into_numpy_array(stream)

                start_time = time.monotonic()
                results = detect_objects(interpreter, image, args.threshold)

                input_tensor = np.expand_dims(image, 0)
                interpreter.invoke()
                results = interpreter.get_output_details()
                elapsed_ms = (time.monotonic() - start_time) * 1000

                annotator.clear()
                annotate_objects(annotator, results, labels)
                annotator.text([5, 0], '%.1fms' % (elapsed_ms))
                annotator.update()

                queue.put(stream.getvalue())

                stream.seek(0)
                stream.truncate()

        finally:
            camera.stop_preview()


def run_video_stream(queue: Queue):
    class CamHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path.endswith('.mjpg'):
                self.send_response(200)
                self.send_header(
                    'Content-type', 'multipart/x-mixed-replace; boundary=--jpgboundary')
                self.end_headers()
                stream = io.BytesIO()
                try:
                    start = time.time()
                    while True:
                        stream_value = queue.get()
                        self.wfile.write(bytes("--jpgboundary", "utf8"))
                        self.send_header('Content-type', 'image/jpeg')
                        self.send_header('Content-length',
                                         len(stream_value))
                        self.end_headers()
                        self.wfile.write(stream_value)
                except KeyboardInterrupt:
                    pass
                return
            else:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(
                    bytes("<html><head></head><body><img src='/cam.mjpg'/></body></html>", "utf8"))
                return

    try:
        server = HTTPServer(('', 8080), CamHandler)
        print("server started")
        server.serve_forever()
    except KeyboardInterrupt:
        server.socket.close()


def main():
    queue = Queue()
    # Producer
    tf_proc = Process(target=run_tensorflow_inference, args=[queue])
    tf_proc.start()

    # Consumer
    video_stream_proc = Process(target=run_video_stream, args=[queue])
    video_stream_proc.start()

    tf_proc.join()


if __name__ == '__main__':
    main()
