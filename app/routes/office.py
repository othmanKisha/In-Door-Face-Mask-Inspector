from flask import redirect, render_template, session, url_for
from config import db


def change_office(office):
    if not session.get("user"):
        return redirect(url_for("login"))
    cams = db.cameras.find({})
    offices = [(cam['office'], cam['label']) for cam in cams]
    return render_template('video/video_feed.html', office=office, offices=offices)
