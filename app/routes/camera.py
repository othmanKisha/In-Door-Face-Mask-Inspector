from model.camera import gen, VideoCamera
from flask import Response
from config import db


def video_feed(office):
    camera = db.cameras.find_one({'office': office})
    frame = gen(VideoCamera(camera['RTSP']))
    return Response(frame, mimetype='multipart/x-mixed-replace; boundary=frame')
    