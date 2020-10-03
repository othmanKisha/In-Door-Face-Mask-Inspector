from flask import Flask, render_template, Response
from model.camera import VideoCamera, gen
from keys import CAMERAS

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/change_office/<string:office>')
def change_office(office):
    return render_template('video_feed.html', id=office)


@app.route('/video_feed/<string:cam_id>')
def video_feed(cam_id):
    frame = gen(VideoCamera(CAMERAS[cam_id]))
    return Response(frame, mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(debug=True)
