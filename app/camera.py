from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from threading import Thread, Timer, Event
from datetime import datetime
import gridfs
import numpy as np
import imutils
import cv2
import io
import os
import time
import config

try:
    from greenlet import getcurrent as get_ident
except ImportError:
    try:
        from thread import get_ident
    except ImportError:
        from _thread import get_ident


class CameraEvent(object):
    """An Event-like class that signals all active clients when a new frame is
    available.
    """

    def __init__(self):
        self.events = {}

    def wait(self):
        """Invoked from each client's thread to wait for the next frame."""
        ident = get_ident()
        if ident not in self.events:
            # this is a new client
            # add an entry for it in the self.events dict
            # each entry has two elements, a threading.Event() and a timestamp
            self.events[ident] = [Event(), time.time()]
        return self.events[ident][0].wait()

    def set(self):
        """Invoked by the camera thread when a new frame is available."""
        now = time.time()
        remove = None
        for ident, event in self.events.items():
            if not event[0].isSet():
                # if this client's event is not set, then set it
                # also update the last set timestamp to now
                event[0].set()
                event[1] = now
            else:
                # if the client's event is already set, it means the client
                # did not process a previous frame
                # if the event stays set for more than 5 seconds, then assume
                # the client is gone and remove it
                if now - event[1] > 5:
                    remove = ident
        if remove:
            del self.events[remove]

    def clear(self):
        """Invoked from each client's thread after a frame was processed."""
        self.events[get_ident()][0].clear()


class BaseCamera(object):
    thread = None  # background thread that reads frames from camera
    frame = None  # current frame is stored here by background thread
    # last_access = 0  # time of last client access to the camera
    event = CameraEvent()

    def __init__(self):
        """Start the background camera thread if it isn't running yet."""
        if BaseCamera.thread is None:
            # BaseCamera.last_access = time.time()

            # start background frame thread
            BaseCamera.thread = Thread(target=self._thread)
            BaseCamera.thread.start()

            # wait until frames are available
            while self.get_frame() is None:
                time.sleep(0)

    def get_frame(self):
        """Return the current camera frame."""
        # BaseCamera.last_access = time.time()

        # wait for a signal from the camera thread
        BaseCamera.event.wait()
        BaseCamera.event.clear()

        return BaseCamera.frame

    @staticmethod
    def frames():
        """"Generator that returns frames from the camera."""
        raise RuntimeError('Must be implemented by subclasses.')

    @classmethod
    def _thread(cls):
        """Camera background thread."""
        print('Starting camera thread.')
        frames_iterator = cls.frames()
        for frame in frames_iterator:
            BaseCamera.frame = frame
            BaseCamera.event.set()  # send signal to clients
            time.sleep(0)

            # if there hasn't been any clients asking for frames in
            # the last 10 seconds then stop the thread
            # if time.time() - BaseCamera.last_access > 10:
            #     frames_iterator.close()
            #     print('Stopping camera thread due to inactivity.')
            #     break
        # BaseCamera.thread = None


class Camera(BaseCamera):
    def __init__(self, source=0):
        Camera.set_video_source(source)
        super(Camera, self).__init__()

    @staticmethod
    def set_video_source(source):
        Camera.video_source = source

    @staticmethod
    def frames():
        camera = cv2.VideoCapture(Camera.video_source)
        flag = False

        if camera.isOpened():
            while True:
                (grabbed, img) = camera.read()
                if not grabbed:
                    break

                img = imutils.resize(img, width=400)
                (locs, preds) = detect_and_predict(img)
                has_violation = False
                Camera.draw_boxes(img, locs, preds, has_violation)

                jpg = cv2.imencode('.jpg', img)[1]
                if has_violation and not flag:
                    flag = True
                    alert_timer = Timer(60, alert_and_store,
                                        args=(jpg, Camera.video_source, flag))
                    alert_timer.start()

                io_buf = io.BytesIO(jpg)
                frame = io_buf.getvalue()
                io_buf.close()
                yield frame

    @staticmethod
    def draw_boxes(img, locs, preds, has_violation):
        for (box, pred) in zip(locs, preds):
            (startX, startY, endX, endY) = box
            (mask, withoutMask) = pred

            label = "Mask" if mask > withoutMask else "No Mask"
            has_violation = True if label == "No Mask" else has_violation
            color = (0, 255, 0) if label == "Mask" else (0, 0, 255)
            label += ": {:.2f}%".format(max(mask, withoutMask) * 100)

            cv2.putText(img, label, (startX, startY - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
            cv2.rectangle(img, (startX, startY), (endX, endY), color, 2)

        return img, has_violation    


def detect_and_predict(frame):
    (faces, locs, preds) = [], [], []
    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), (104.0, 177.0, 123.0))
    config.faceNet.setInput(blob)
    detections = config.faceNet.forward()

    for i in range(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]

        if confidence > config.CONFIDENCE:
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
        preds = config.maskNet.predict(faces, batch_size=32)

    return (locs, preds)


def alert_and_store(jpg, source, flag):
    text = MIMEText("This email is being sent to test the functionality of the program")
    image = MIMEImage(jpg, name="ViolationPic.jpg")

    cams = config.db['cameras'].find({'RTSP': source})
    # To = {cam['supervisor_email'] for cam in cams}
    To = ['o.kisha2014@gmail.com']

    msg = MIMEMultipart()
    msg['Subject'] = 'IDFMI Alert'
    msg['From'] = config.EMAIL_ADDRESS
    msg['To'] = To
    msg.attach(text)
    msg.attach(image)

    config.smtp.ehlo()
    config.smtp.starttls()
    config.smtp.ehlo()

    config.smtp.login(config.EMAIL_ADDRESS, config.EMAIL_PASSWORD)
    config.smtp.sendmail(config.EMAIL_ADDRESS, To, msg.as_string())
    config.smtp.quit()

    # searching for the location of the camera
    camera = config.db['cameras'].find_one({'RTSP': source})
    roomName = camera['office']

    fs = gridfs.GridFS(config.db)  # gridFS instance
    # converting the image to bytes
    io_buf = io.BytesIO(jpg)
    frame = io_buf.getvalue()
    io_buf.close()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # get time
    fs.put(frame, date=now, room=roomName)  # save image into DB.

    flag = False
