from flask import Flask, redirect, render_template, request, session, url_for, Response
from flask_session import Session  # https://pythonhosted.org/Flask-Session
from werkzeug.middleware.proxy_fix import ProxyFix
import requests
import uuid
import msal
import config
from camera import Camera


app = Flask(__name__)
app.config.from_object(config)
Session(app)

# This section is needed for url_for("foo", _external=True) to automatically
# generate http scheme when this sample is running on localhost,
# and to generate https scheme when it is deployed behind reversed proxy.
# See also https://flask.palletsprojects.com/en/1.0.x/deploying/wsgi-standalone/#proxy-setups
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)


@app.route("/")
def index():
    if not session.get("user"):
        return redirect(url_for("login"))
    cams = config.db['cameras'].find({})
    cam_set = set()
    offices = []
    for cam in cams:
        offices.append((cam['office'], cam['label']))
        cam_set.add(cam['RTSP'])
    for cam in cam_set:
        Camera(cam)
    return render_template('index.html', offices=offices)


@app.route("/create/<string:office>/<string:label>")
def create(office, label):
    if not session.get("user"):
        return redirect(url_for("login"))
    RTSP = "rtsp://192.168.100.13:8080/h264_ulaw.sdp"
    config.db['cameras'].insert_one({
        'RTSP': RTSP,
        'office': office,
        'label': label
    })
    Camera(RTSP)
    return redirect(url_for('index'))


@app.route('/change_office/<string:office>')
def change_office(office):
    if not session.get("user"):
        return redirect(url_for("login"))
    cams = config.db['cameras'].find({})
    offices = [(cam['office'], cam['label']) for cam in cams]
    return render_template('camera/video_feed.html', office=office, offices=offices)


@app.route('/video_feed/<string:office>')
def video_feed(office):
    if not session.get("user"):
        return redirect(url_for("login"))
    cam = config.db['cameras'].find_one({'office': office})
    frame = gen(Camera(cam['RTSP']))
    return Response(frame, mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route("/login")
def login():
    session["state"] = str(uuid.uuid4())
    # Technically we could use empty list [] as scopes to do just sign in,
    # here we choose to also collect end user consent upfront
    auth_url = _build_auth_url(scopes=config.SCOPE, state=session["state"])
    return render_template("auth/login.html", auth_url=auth_url, version=msal.__version__)


@app.route("/logout")
def logout():
    # Wipe out user and its token cache from session
    session.clear()
    # Also logout from your tenant's web session
    return redirect(config.AUTHORITY + "/oauth2/v2.0/logout" +
                    "?post_logout_redirect_uri=" + url_for("index", _external=True))


@app.route("/graphcall")
def graphcall():
    token = _get_token_from_cache(config.SCOPE)
    if not token:
        return redirect(url_for("login"))
    # Use token to call downstream service
    graph_data = requests.get(
        config.ENDPOINT,
        headers={'Authorization': 'Bearer ' + token['access_token']},
    ).json()
    return render_template('auth/display.html', result=graph_data)


@app.route(config.REDIRECT_PATH)
def authorized():
    if request.args.get('state') != session.get("state"):
        # No-OP. Goes back to Index page
        return redirect(url_for("index"))
    # Authentication/Authorization failure
    if "error" in request.args:
        return render_template("auth/auth_error.html", result=request.args)
    if request.args.get('code'):
        cache = _load_cache()
        result = _build_msal_app(cache=cache).acquire_token_by_authorization_code(
            request.args['code'],
            # Misspelled scope would cause an HTTP 400 error here
            scopes=config.SCOPE,
            redirect_uri=url_for("authorized", _external=True))
        if "error" in result:
            return render_template("auth/auth_error.html", result=result)
        session["user"] = result.get("id_token_claims")
        _save_cache(cache)
    return redirect(url_for("index"))


def _load_cache():
    cache = msal.SerializableTokenCache()
    if session.get("token_cache"):
        cache.deserialize(session["token_cache"])
    return cache


def _save_cache(cache):
    if cache.has_state_changed:
        session["token_cache"] = cache.serialize()


def _build_msal_app(cache=None, authority=None):
    return msal.ConfidentialClientApplication(
        config.CLIENT_ID, authority=authority or config.AUTHORITY,
        client_credential=config.CLIENT_SECRET, token_cache=cache)


def _build_auth_url(authority=None, scopes=None, state=None):
    return _build_msal_app(authority=authority).get_authorization_request_url(
        scopes or [],
        state=state or str(uuid.uuid4()),
        redirect_uri=url_for("authorized", _external=True))


def _get_token_from_cache(scope=None):
    # This web app maintains one cache per session
    cache = _load_cache()
    cca = _build_msal_app(cache=cache)
    accounts = cca.get_accounts()
    # So all account(s) belong to the current signed-in user
    if accounts:
        result = cca.acquire_token_silent(scope, account=accounts[0])
        _save_cache(cache)
        return result


def gen(camera):
    try:
        while True:
            frame = camera.get_frame()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
    except Exception:
        yield ''


# Used in template
app.jinja_env.globals.update(_build_auth_url=_build_auth_url)


if __name__ == "__main__":
    cams = config.db['cameras'].find({})
    cam_set = set()
    for cam in cams:
        if not cam['RTSP'] in cam_set:
            cam_set.add(cam['RTSP'])
            Camera(cam['RTSP'])
    app.run(host='0.0.0.0', threaded=True)
