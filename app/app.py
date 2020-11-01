from flask import Flask, render_template, session, redirect, url_for
from flask_session import Session  
from werkzeug.middleware.proxy_fix import ProxyFix
from model.camera import VideoCamera
import routes.helpers.auth as authHelpers
import routes.camera as cameraRoutes
import routes.office as officeRoutes
import routes.auth as authRoutes
import config


app = Flask(__name__)
app.config.from_object(config)
app.jinja_env.globals.update(_build_auth_url=authHelpers._build_auth_url)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
Session(app)


@app.route("/")
def index():
    if not session.get("user"):
        return redirect(url_for("login"))
    cams = config.db.cameras.find({})
    offices = [(cam['office'], cam['label']) for cam in cams]
    return render_template('index.html', offices=offices)

@app.route('/change_office/<string:office>')
def change_office(office): return officeRoutes.change_office(office) 

@app.route('/video_feed/<string:office>')
def video_feed(office): return cameraRoutes.video_feed(office) 

@app.route("/login")
def login(): return authRoutes.login()

@app.route("/logout")
def logout(): return authRoutes.logout()

@app.route("/graphcall") 
def graphcall(): return authRoutes.graphcall()

@app.route(config.REDIRECT_PATH)
def authorized(): return authRoutes.authorized()


if __name__ == "__main__":
    app.run(host='0.0.0.0')
