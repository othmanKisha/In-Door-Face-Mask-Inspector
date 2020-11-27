# -*- encoding=utf-8 -*-
# Authentication is inspired from the tutorial by Microsoft form azure active
# directory authentication.
# Tutorial Source: https://github.com/rebremer/ms-identity-python-webapp-backend
import msal
import uuid
import config
import requests
import functools
from camera import Camera
from flask_session import Session
import flask_monitoringdashboard as dashboard
from werkzeug.middleware.proxy_fix import ProxyFix
from flask import (Flask,
                   flash,
                   redirect,
                   render_template,
                   request,
                   Response,
                   session,
                   url_for
                   )


app = Flask(__name__)
app.config.from_object(config)
Session(app)
dashboard.bind(app)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
cameras_collection = config.db['cameras']
security_collection = config.db['security']


def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user"):
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def generate(camera):
    while True:
        frame = camera.get_frame()
        if frame is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' +
                   frame + b'\r\n\r\n'
                   )


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
        config.CLIENT_ID,
        authority=authority or config.AUTHORITY,
        client_credential=config.CLIENT_SECRET,
        token_cache=cache
    )


def _build_auth_url(authority=None, scopes=None, state=None):
    return _build_msal_app(authority=authority).get_authorization_request_url(
        scopes or [],
        state=state or str(uuid.uuid4()),
        redirect_uri=url_for("authorized", _external=True)
    )


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


@app.route("/", methods=['GET'])
@login_required
def index():
    """
    index route
    :param:
    :return: home template which takes the list of all security 
             members in addition the list of all cameras.
    """
    cameras = list(cameras_collection.find({}))
    security = list(security_collection.find({}))
    return render_template('pages/home.html',
                           cameras=cameras,
                           security=security
                           )


@app.route("/create/camera", methods=['POST'])
@login_required
def create_camera():
    """
    create camera route
    :param location: the location of the camera retreived from the form.
    :param url: the rtsp url of the camera retreived from the form.
    :param status: the status (Working, Stopped) of the camera 
                   retreived from the form.
    :param supervisor: the _id of security memeber selected in the form.
    :return redirect: go to root route with flash of success or failure. 
    """
    _id = uuid.uuid4()  # generate a unique id for the record
    data = request.form.copy()
    # In case we want to use webcam
    # url = int(data.get('url')) if data.get('url') == '0' or data.get('url') == '1' else data.get('url')
    try:
        if len(list(security_collection.find({}))) < 1:
            raise Exception
        cameras_collection.insert_one({
            "_id": _id,
            "location": data.get('location'),
            "url": data.get('url'),
            "status": data.get('status'),
            "supervisor_id": data.get('supervisor_id')
        })
        flash(
            f"success|Camera at {data.get('location')} has been successfully added.")
    except:
        flash(f"danger|Camera couldn't be added")
    finally:
        return redirect(url_for("index"))


@app.route("/create/security", methods=['POST'])
@login_required
def create_security():
    """
    index route
    :param:
    :return: 
    """
    _id = uuid.uuid4()
    data = request.form.copy()
    try:
        security_collection.insert_one({
            "_id": _id,
            "first_name": data.get('first_name'),
            "last_name": data.get('last_name'),
            "email": data.get('email'),
            "phone": data.get('phone')
        })
        flash(
            f"success|Security member {data.get('first_name')} {data.get('last_name')} has been successfully added.")
    except:
        flash(f"danger|Security member couldn't be added")
    finally:
        return redirect(url_for("index"))


@app.route("/edit/camera/<uuid:id>", methods=['POST'])
@login_required
def edit_camera(id):
    """
    index route
    :param:
    :return: 
    """
    data = request.form.copy()
    # In case we want to use webcam
    # url = int(data.get('url')) if data.get('url') == '0' or data.get('url') == '1' else data.get('url')
    try:
        cameras_collection.update_one({"_id": id}, {"$set": {
            "location": data.get('location'),
            "url": data.get('url'),
            "status": data.get('status'),
            "supervisor_id": data.get('supervisor_id')
        }})
        flash("success|Camer has been successfully updated.")
    except:
        flash("danger|Camera couldn't be updated")
    finally:
        return redirect(url_for("index"))


@app.route("/edit/security/<uuid:id>", methods=['POST'])
@login_required
def edit_security(id):
    """
    index route
    :param:
    :return: 
    """
    data = request.form.copy()
    try:
        security_collection.update_one({"_id": id}, {"$set": {
            "first_name": data.get('first_name'),
            "last_name": data.get('last_name'),
            "email": data.get('email'),
            "phone": data.get('phone')
        }})
        flash(f"success|Security member has been successfully updated.")
    except:
        flash(f"danger|Security member couldn't be updated")
    finally:
        return redirect(url_for("index"))


@app.route("/delete/camera/<uuid:id>", methods=['POST'])
@login_required
def delete_camera(id):
    """
    index route
    :param:
    :return: 
    """
    try:
        cameras_collection.delete_one({"_id": id})
        flash(f"success|Camera has been successfully deleted.")
    except:
        flash(f"danger|Camera couldn't be deleted")
    finally:
        return redirect(url_for("index"))


@app.route("/delete/security/<uuid:id>", methods=['POST'])
@login_required
def delete_security(id):
    """
    index route
    :param:
    :return: 
    """
    try:
        cameras_collection.update_many(
            {'supervisor_id': str(id)},
            {'$set': {
                'supervisor_id': -1
            }})
        security_collection.delete_one({"_id": id})
        flash(f"success|Security member has been successfully deleted.")
    except:
        flash(f"danger|Security member couldn't be deleted")
    finally:
        return redirect(url_for("index"))


@app.route('/video/feed/<uuid:id>')
@login_required
def video_feed(id):
    """
    index route
    :param:
    :return: 
    """
    try:
        return Response(generate(Camera(id)),
                        mimetype='multipart/x-mixed-replace; boundary=frame'
                        )
    except:
        flash("danger|There is no camera with this id")
        return redirect(url_for('index'))


@app.route("/login")
def login():
    """
    index route
    :param:
    :return: 
    """
    session["state"] = str(uuid.uuid4())
    # Technically we could use empty list [] as scopes to do just sign in,
    # here we choose to also collect end user consent upfront
    auth_url = _build_auth_url(
        scopes=config.SCOPE, state=session["state"]
    )
    return render_template("pages/welcome.html", auth_url=auth_url)


@app.route("/logout")
def logout():
    """
    index route
    :param:
    :return: 
    """
    # Wipe out user and its token cache from session
    session.clear()
    # Also logout from your tenant's web session
    return redirect(config.AUTHORITY +
                    "/oauth2/v2.0/logout" +
                    "?post_logout_redirect_uri=" +
                    url_for("index", _external=True)
                    )


@app.route(config.REDIRECT_PATH)
def authorized():
    """
    index route
    :param:
    :return: 
    """
    if request.args.get('state') != session.get("state"):
        # No-OP. Goes back to Index page
        return redirect(url_for("index"))
    # Authentication/Authorization failure
    if "error" in request.args:
        return render_template("auth_error.html", result=request.args)
    if request.args.get('code'):
        cache = _load_cache()
        result = _build_msal_app(cache=cache).acquire_token_by_authorization_code(
            request.args['code'],
            # Misspelled scope would cause an HTTP 400 error here
            scopes=config.SCOPE,
            redirect_uri=url_for("authorized", _external=True)
        )
        if "error" in result:
            return render_template("auth_error.html", result=result)
        session["user"] = result.get("id_token_claims")
        _save_cache(cache)
    return redirect(url_for("index"))


if __name__ == "__main__":
    # Run the server
    app.run(host='0.0.0.0', threaded=True)
