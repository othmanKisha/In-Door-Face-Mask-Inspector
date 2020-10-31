from flask import Flask, render_template, session, redirect, url_for, Response
from flask_session import Session  # https://pythonhosted.org/Flask-Session
from werkzeug.middleware.proxy_fix import ProxyFix
from model.camera import VideoCamera
import routes.helpers.auth as authHelpers
import routes.video as videoRoutes
import routes.index as indexRoute
import routes.auth as authRoutes
import app_config


app = Flask(__name__)
app.config.from_object(app_config)
app.jinja_env.globals.update(_build_auth_url=authHelpers._build_auth_url)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
Session(app)

@app.route("/")
def index(): return indexRoute.index()

@app.route('/change_office/<string:office>')
def change_office(office): return videoRoutes.change_office(office) 

@app.route('/video_feed/<string:office>')
def video_feed(office): return videoRoutes.video_feed(office) 

@app.route("/login")
def login(): return authRoutes.login()

@app.route("/logout")
def logout(): return authRoutes.logout()

@app.route("/graphcall") 
def graphcall(): return authRoutes.graphcall()

@app.route(app_config.REDIRECT_PATH)
def authorized(): return authRoutes.authorized()


if __name__ == "__main__":
    app.run(host='0.0.0.0')
