# -*- encoding=utf-8 -*-
# Took and modified the BaseCamera and CameraEvent classes, and changed the Cmaera Class
# Original Source: https://blog.miguelgrinberg.com/post/flask-video-streaming-revisited
# Original Code Repository: https://github.com/miguelgrinberg/flask-video-streaming
# Modified a little bit in inference method from face mask detection repository
# Code of inference: https://github.com/AIZOOTech/FaceMaskDetection
import io
import os
import cv2
import time
import gridfs
import config
import numpy as np
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from threading import Thread, Timer, Event
from model.load_model import tf_inference
from email.mime.multipart import MIMEMultipart
from model.utils import decode_bbox, single_class_non_max_suppression

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
    event = CameraEvent()

    def __init__(self):
        """Start the background camera thread if it isn't running yet."""
        if BaseCamera.thread is None:
            # start background frame thread
            BaseCamera.thread = Thread(target=self._thread)
            BaseCamera.thread.start()

            # wait until frames are available
            while self.get_frame() is None:
                time.sleep(0)

    def get_frame(self):
        """Return the current camera frame."""
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


class Camera(BaseCamera):
    def __init__(self, source=0):
        """
        index route
        :param:
        :return: 
        """
        Camera.set_video_source(source)
        super(Camera, self).__init__()

    @staticmethod
    def set_video_source(source):
        """
        index route
        :param:
        :return: 
        """
        Camera.video_source = source

    @staticmethod
    def frames():
        """
        index route
        :param:
        :return: 
        """
        camera = cv2.VideoCapture(Camera.video_source)
        height = camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
        width = camera.get(cv2.CAP_PROP_FRAME_WIDTH)
        fps = camera.get(cv2.CAP_PROP_FPS)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        total_frames = camera.get(cv2.CAP_PROP_FRAME_COUNT)
        flag = False
        status = True

        if camera.isOpened():
            while status:
                (status, img) = camera.read()
                if status:
                    has_violation = False
                    inference(img,
                              has_violation,
                              config.CONFIDENCE,
                              iou_thresh=0.5,
                              target_shape=(260, 260),
                              draw_result=True
                              )

                    jpg = cv2.imencode('.jpg', img)[1]
                    if has_violation and not flag:
                        flag = True
                        alert_timer = Timer(60, 
                                            alert_and_store,
                                            args=(jpg, Camera.video_source, flag)
                                            )
                        alert_timer.start()

                    io_buf = io.BytesIO(jpg)
                    frame = io_buf.getvalue()
                    io_buf.close()
                    yield frame


def inference(image,
              has_violation,
              conf_thresh=0.5,
              iou_thresh=0.4,
              target_shape=(160, 160),
              draw_result=True
              ):
    '''
    Main function of detection inference
    :param image: 3D numpy array of image
    :param conf_thresh: the min threshold of classification probabity.
    :param iou_thresh: the IOU threshold of NMS
    :param target_shape: the model input size.
    :param draw_result: whether to daw bounding box to the image.
    :param show_result: whether to display the image.
    :return:
    '''
    height, width, _ = image.shape
    image_resized = cv2.resize(image, target_shape)
    image_np = image_resized / 255.0
    image_exp = np.expand_dims(image_np, axis=0)
    y_bboxes_output, y_cls_output = tf_inference(
        config.SESS, config.GRAPH, image_exp
        )

    # remove the batch dimension, for batch is always 1 for inference.
    y_bboxes = decode_bbox(config.ANCHORS_EXP, y_bboxes_output)[0]
    y_cls = y_cls_output[0]
    # To speed up, do single class NMS, not multiple classes NMS.
    bbox_max_scores = np.max(y_cls, axis=1)
    bbox_max_score_classes = np.argmax(y_cls, axis=1)

    # keep_idx is the alive bounding box after nms.
    keep_idxs = single_class_non_max_suppression(y_bboxes,
                                                 bbox_max_scores,
                                                 conf_thresh=conf_thresh,
                                                 iou_thresh=iou_thresh,
                                                 )

    for idx in keep_idxs:
        conf = float(bbox_max_scores[idx])
        class_id = bbox_max_score_classes[idx]
        bbox = y_bboxes[idx]
        # clip the coordinate, avoid the value exceed the image boundary.
        xmin = max(0, int(bbox[0] * width))
        ymin = max(0, int(bbox[1] * height))
        xmax = min(int(bbox[2] * width), width)
        ymax = min(int(bbox[3] * height), height)

        if draw_result:
            if class_id == 0:
                color = (0, 255, 0)
            else:
                has_violation = True
                color = (0, 0, 255)
            cv2.rectangle(image, (xmin, ymin), (xmax, ymax), color, 2)
            cv2.putText(image, "%s: %.2f" % (config.ID2CLASS[class_id], conf), 
                                            (xmin + 2, ymin - 2),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, 
                                            color
                                            )


def alert_and_store(jpg, source, flag):
    """
    index route
    :param:
    :return: 
    """
    cam = config.db['cameras'].find_one({'url': source})
    if cam['supervisor_id'] != -1:
        sec = config.db['security'].find_one({'_id': cam['supervisor_id']})
        To = [sec['email']]

        msg = MIMEMultipart()
        msg['Subject'] = 'IDFMI Alert'
        msg['From'] = config.EMAIL_ADDRESS
        msg['To'] = To
        text = MIMEText(
            f"""
            Dear Mr. {sec['last_name']},

            We have detected a violation on {cam['location']}. You can find
            the violation picture attached with this email. Please check
            the picture.

            regards,
            IDFMI Team
            """
            )
        image = MIMEImage(jpg, name="ViolationPic.jpg")
        msg.attach(text)
        msg.attach(image)

        config.smtp.ehlo()
        config.smtp.starttls()
        config.smtp.ehlo()

        config.smtp.login(config.EMAIL_ADDRESS, config.EMAIL_PASSWORD)
        config.smtp.sendmail(config.EMAIL_ADDRESS, To, msg.as_string())
        config.smtp.quit()

    # searching for the location of the camera
    roomName = cam['location']

    fs = gridfs.GridFS(config.db)  # gridFS instance
    # converting the image to bytes
    io_buf = io.BytesIO(jpg)
    frame = io_buf.getvalue()
    io_buf.close()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # get time
    fs.put(frame, date=now, room=roomName)  # save image into DB.

    flag = False


def generate(camera):
    """
    index route
    :param:
    :return: 
    """
    while True:
        frame = camera.get_frame()
        if frame is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + 
                   frame + b'\r\n\r\n'
                   )
