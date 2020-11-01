from flask import redirect, Response, session, url_for
from model.camera import gen, VideoCamera
from config import db


def video_feed(office):
    if not session.get("user"):
        return redirect(url_for("login"))
    camera = db.cameras.find_one({'office': office})
    frame = gen(VideoCamera(camera['RTSP']))
    return Response(frame, mimetype='multipart/x-mixed-replace; boundary=frame')
    