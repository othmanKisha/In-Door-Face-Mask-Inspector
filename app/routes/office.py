from flask import render_template
from config import db


def change_office(office):
    cams = db.cameras.find({})
    offices = [(cam['office'], cam['label']) for cam in cams]
    return render_template('video/video_feed.html', office=office, offices=offices)
