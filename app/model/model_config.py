from tensorflow.keras.models import load_model
import cv2
import os


args = {
    "directory": "model",
    "face": "face_detector",
    "model": "mask_detector",
    "weightsFile": "res10_300x300_ssd_iter_140000.caffemodel",
    "prototxtFile": "deploy.prototxt",
    "modelFile": "mask_detector.model",
    "confidence": 0.5
}


faceNet = cv2.dnn.readNet(
    os.path.sep.join([args["directory"], args["face"], args["prototxtFile"]]),
    os.path.sep.join([args["directory"], args["face"], args["weightsFile"]])
)


maskNet = load_model(
    os.path.sep.join([args["directory"], args["model"], args["modelFile"]])
)
