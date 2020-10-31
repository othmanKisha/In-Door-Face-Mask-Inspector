from flask import redirect, render_template, session, url_for
from app_config import cameras


def index():
    if not session.get("user"):
        return redirect(url_for("login"))
    cams = cameras.find({})
    offices = [(cam['office'], cam['label']) for cam in cams]
    return render_template('index.html', offices=offices)
