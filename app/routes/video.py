from flask import redirect, render_template, Response, session, url_for
from model.camera import gen, VideoCamera
from app_config import cameras


def change_office(office):
    if not session.get("user"):
        return redirect(url_for("login"))
    cams = cameras.find({})
    offices = [(cam['office'], cam['label']) for cam in cams]
    return render_template('video/video_feed.html', office=office, offices=offices)


def video_feed(office):
    if not session.get("user"):
        return redirect(url_for("login"))
    camera = cameras.find_one({'office': office})
    frame = gen(VideoCamera(camera['RTSP']))
    return Response(frame, mimetype='multipart/x-mixed-replace; boundary=frame')
