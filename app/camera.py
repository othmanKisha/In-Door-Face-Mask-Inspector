# -*- coding: utf-8 -*-
# From https://github.com/miguelgrinberg/flask-video-streaming
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import numpy as np
import cv2
import imutils
import gridfs
import PIL.Image as Image
import threading
import time
import os
import io
#ByteIO is better than > Pickle > tostring > etc...
from datetime import datetime
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
            self.events[ident] = [threading.Event(), time.time()]
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
    thread = {}  # background thread that reads frames from camera
    frame = {}  # current frame is stored here by background thread
    last_access = {}  # time of last client access to the camera
    event = {}
    running = {}

    def __init__(self, unique_id=None):
        """Start the background camera thread if it isn't running yet."""
        self.unique_id = unique_id
        BaseCamera.event[self.unique_id] = CameraEvent()
        BaseCamera.running[self.unique_id] = True

        if self.unique_id not in BaseCamera.thread:
            BaseCamera.thread[self.unique_id] = None

        if BaseCamera.thread[self.unique_id] is None:
            BaseCamera.last_access[self.unique_id] = time.time()

            # start background frame thread
            BaseCamera.thread[self.unique_id] = threading.Thread(
                target=self._thread, args=(self.unique_id,))
            BaseCamera.thread[self.unique_id].start()

            # wait until frames are available
            while self.get_frame() is None:
                time.sleep(0)

    def get_frame(self):
        """Return the current camera frame."""
        BaseCamera.last_access[self.unique_id] = time.time()

        # wait for a signal from the camera thread
        BaseCamera.event[self.unique_id].wait()
        BaseCamera.event[self.unique_id].clear()

        return BaseCamera.frame[self.unique_id]

    @staticmethod
    def frames():
        """"Generator that returns frames from the camera."""
        raise RuntimeError('Must be implemented by subclasses')

    @classmethod
    def _thread(cls, unique_id):
        """Camera background thread."""
        frames_iterator = cls.frames()
        for frame in frames_iterator:
            BaseCamera.frame[unique_id] = frame
            BaseCamera.event[unique_id].set()  # send signal to clients
            time.sleep(0)

            # if there haven't been any clients asking for frames in
            # the last 10 seconds then stop the thread
            if time.time() - BaseCamera.last_access[unique_id] > 10:
                frames_iterator.close()
                break
            if not BaseCamera.running[unique_id]:
                frames_iterator.close()
                break

        BaseCamera.thread[unique_id] = None
        BaseCamera.running[unique_id] = False

    @staticmethod
    def stop(unique_id):
        BaseCamera.running[unique_id] = False

    @staticmethod
    def is_running(unique_id):
        return BaseCamera.running[unique_id]


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
        detection_timer = 0
        detected = False

        if not camera.isOpened():
            raise RuntimeError('Could not start camera.')

        while True:
            # read current frame
            _, img = camera.read()
            img = imutils.resize(img, width=400)
            (locs, preds) = detect_and_predict_mask(
                img, config.FACE_NET, config.MASK_NET)

            violation = False
            for (box, pred) in zip(locs, preds):
                (startX, startY, endX, endY) = box
                (mask, withoutMask) = pred
                label = "Mask" if mask > withoutMask else "No Mask"
                violation = True if label == "No Mask" else violation
                color = (0, 255, 0) if label == "Mask" else (0, 0, 255)
                label += ": {:.2f}%".format(max(mask, withoutMask) * 100)
                cv2.putText(img, label, (startX, startY - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
                cv2.rectangle(img, (startX, startY), (endX, endY), color, 2)

            jpg = cv2.imencode('.jpg', img)[1].tobytes()
            if violation:
                if detection_timer == 0:
                    if not detected:
                        detected = True
                        detection_timer = 60
                    else:
                        detected = False
                        SendMail(jpg, Camera.video_source)
                        StoreImage(jpg)
                else:
                    detection_timer -= 1
            else:
                detected = False
                detection_timer = 0

            # encode as a jpeg image and return it
            time.sleep(0.05)
            yield jpg


def detect_and_predict_mask(frame, faceNet, maskNet):
    (faces, locs, preds) = [], [], []
    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), (104.0, 177.0, 123.0))
    faceNet.setInput(blob)
    detections = faceNet.forward()

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
        preds = maskNet.predict(faces, batch_size=32)

    return (locs, preds)


def gen(camera):
    try:
        while True:
            frame = camera.get_frame()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
    except Exception:
        yield ''


def SendMail(jpg, rtsp):
    # img_data = open(ImgFileName,'rb').read()
    msg = MIMEMultipart()
    msg['Subject'] = 'IDFMI Alert'
    cams = config.db['cameras'].find({'RTSP': rtsp})
    To = {cam['supervisor_email'] for cam in cams}
    # To = {'s201651740@kfupm.edu.sa','medo111.2018@gmail.com'}

    text = MIMEText("""
        This email is being sent to test the functionality of the program
    """)
    msg.attach(text)
    # image = MIMEImage(img_data, name=os.path.basename(ImgFileName))
    image = MIMEImage(jpg, name="ViolationPic.jpg")
    msg.attach(image)
    # password = input(str("Enter your password: "))

    config.smtp.ehlo()
    config.smtp.starttls()
    config.smtp.ehlo()
    config.smtp.login(config.EMAIL_ADDRESS, config.EMAIL_PASSWORD)
    config.smtp.sendmail(config.EMAIL_ADDRESS, To, msg.as_string())
    config.smtp.quit()


def StoreImage(jpg):
    # gridFS instance
    fs = gridfs.GridFS(config.db)

    # read the image as a byte
    # img = cv2.imread("test.jpg")
    pil_image = Image.fromarray(jpg)

    #Convert array to image
    b = io.BytesIO()
    pil_image.save(b, 'jpeg')
    im_bytes = b.getvalue()
    b.close()

    #save image into DB.
    imageID = fs.put(im_bytes)

    #get time
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # print(now)

    #define meta data
    meta = {
        'name': 'Violations',
        'images': [
            {
                'imageID': imageID,
                'time': now
            }
        ]
    }

    #store meta data
    config.db['Violation_pic'].insert_one(meta)

    # get the image meta data
    # image = config.db['Violation_pic'].find_one({'name': 'Violations'})['images'][0]

    # # get the image from gridfs
    # gOut = fs.get(image['imageID'])

    # # convert bytes to ndarray
    # read_pil_image = Image.open(io.BytesIO(gOut.read()))
    # array = np.array(read_pil_image)
    # print(array)
