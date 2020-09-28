from detect_predict import detect_and_predict_mask
from model_process import faceNet, maskNet
from imutils.video import VideoStream
import imutils
import time
import cv2


class VideoCamera(object):
    def __init__(self):
        self.video = VideoStream(src=0).start()
        time.sleep(2.0)

    def __del__(self):
        self.video.stop()

    def get_frame(self):
        frame = self.video.read()
        frame = imutils.resize(frame, width=400)
        (locs, preds) = detect_and_predict_mask(frame, faceNet, maskNet)

        for (box, pred) in zip(locs, preds):
            (startX, startY, endX, endY) = box
            (mask, withoutMask) = pred

            label = "Mask" if mask > withoutMask else "No Mask"
            color = (0, 255, 0) if label == "Mask" else (0, 0, 255)
            label = "{}: {:.2f}%".format(label, max(mask, withoutMask) * 100)

            cv2.putText(frame, label, (startX, startY - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
            cv2.rectangle(frame, (startX, startY), (endX, endY), color, 2)

        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()
