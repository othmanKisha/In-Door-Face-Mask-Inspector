from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
import numpy as np
import argparse
import cv2
import os


weightsFile = "res10_300x300_ssd_iter_140000.caffemodel"
prototxtFile = "deploy.prototxt"

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-f", "--face", type=str, default="face_detector")
ap.add_argument("-m", "--model", type=str, default="mask_detector.model")
ap.add_argument("-c", "--confidence", type=float, default=0.5)
args = vars(ap.parse_args())

prototxtPath = os.path.sep.join(["model", args["face"], prototxtFile])
weightsPath = os.path.sep.join(["model", args["face"], weightsFile])

faceNet = cv2.dnn.readNet(prototxtPath, weightsPath)
maskNet = load_model(os.path.sep.join(["model", args["model"]]))


def detect_and_predict_mask(frame, faceNet, maskNet):
    (faces, locs, preds) = [], [], []
    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), (104.0, 177.0, 123.0))
    faceNet.setInput(blob)
    detections = faceNet.forward()

    for i in range(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]

        if confidence > args["confidence"]:
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")

            (startX, startY) = (max(0, startX), max(0, startY))
            (endX, endY) = (min(w - 1, endX), min(h - 1, endY))

            face = frame[startY:endY, startX:endX]
            face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
            face = cv2.resize(face, (224, 224))
            face = img_to_array(face)
            face = preprocess_input(face)

            faces.append(face)
            locs.append((startX, startY, endX, endY))

    if len(faces) > 0:
        faces = np.array(faces, dtype="float32")
        preds = maskNet.predict(faces, batch_size=32)

    return (locs, preds)
