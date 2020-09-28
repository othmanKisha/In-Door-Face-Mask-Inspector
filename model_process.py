from tensorflow.keras.models import load_model
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

prototxtPath = os.path.sep.join([args["face"], prototxtFile])
weightsPath = os.path.sep.join([args["face"], weightsFile])

faceNet = cv2.dnn.readNet(prototxtPath, weightsPath)
maskNet = load_model(args["model"])
