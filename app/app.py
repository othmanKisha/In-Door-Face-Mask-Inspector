from wtforms import SubmitField, StringField, validators, IntegerField, FieldList, FormField
from flask import Flask, redirect, render_template, request, Response, session, url_for
from werkzeug.middleware.proxy_fix import ProxyFix
import flask_monitoringdashboard as dashboard
from flask_bootstrap import Bootstrap
from flask_session import Session
from flask_wtf import FlaskForm
import functools
import requests
import msal
import uuid
import config
from camera import Camera


app = Flask(__name__)
app.config.from_object(config)
Session(app)
Bootstrap(app)
dashboard.bind(app)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)


class RegForm(FlaskForm):
    name_first = StringField('First Name', [validators.DataRequired()])
    name_last = StringField('Last Name', [validators.DataRequired()])
    email = StringField('Email Address', [
        validators.DataRequired(),
        validators.Email(),
        validators.Length(min=6, max=35)])
    phone_number = IntegerField('Phone Number', [validators.DataRequired()])
    number_cams = IntegerField('Numbers of Cameras', [
                               validators.NumberRange(min=1, max=100)])
    submit = SubmitField('Submit')


class CamsLinks(FlaskForm):
    """A form for one or more addresses"""
    name = StringField('unique name', [validators.DataRequired()])
    location = StringField('location', [validators.DataRequired()])
    url = StringField('url', [validators.DataRequired()])


class GenerateFields(FlaskForm):
    list = FieldList(FormField(CamsLinks))
    submit = SubmitField('Submit')


def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user"):
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def UploadCustom(first_name, last_name, email, phone, cams_number):
    # Clean/Empty Current Customization
    config.db['customization'].delete_many({})
    # upload
    config.db['customization'].insert_one({
        'name': 'Settings',
        'Data': [{
            'name_first': first_name,
            'name_last': last_name,
            'Email': email,
            'Phone_Number': phone,
            'Number_Cams': cams_number
        }]})


def UploadLinks(cams_data, num_cams):
    # Clean/Empty Current Customization
    config.db['customization'].delete_many({'Alias': 'Security'})
    Cut = []
    # create dictionary
    for i in range(int(num_cams)):
        Cut.append(cams_data[i])

    for i in range(len(Cut)):
        config.db['customization'].insert_one({
            'Alias': "Security",
            'name': Cut[i]['name'],
            'url': Cut[i]['url'],
            'location': Cut[i]['location']
        })
        

def generate(camera):
    while True:
        frame = camera.get_frame()
        if frame is not None:
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


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


@app.route("/")
@login_required
def index():
    cams = config.db['cameras'].find({})
    offices = [(cam['office'], cam['label']) for cam in cams]
    return render_template('index.html', offices=offices)


@app.route('/change_office/<string:office>')
@login_required
def change_office(office):
    cams = config.db['cameras'].find({})
    offices = [(cam['office'], cam['label']) for cam in cams]
    return render_template('camera/video_feed.html', office=office, offices=offices)


@app.route('/video_feed/<string:office>')
@login_required
def video_feed(office):
    cam = config.db['cameras'].find_one({'office': office})
    return Response(generate(Camera(cam['RTSP'])), 
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/reg', methods=['GET', 'POST'])
@login_required
def registration():
    form = RegForm(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        cams = form.number_cams.data
        UploadCustom(form.name_first.data, form.name_last.data,
                     form.email.data, form.phone_number.data, cams)
        return redirect(url_for('camera', cams=cams))
    return render_template('customization/registration_custom.html', form=form)


@app.route('/cams', methods=['GET', 'POST'])
@login_required
def camera():
    cams = request.args.get('cams')
    print(cams)
    form = GenerateFields(request.form)
    for i in range(int(cams)):
        form.list.append_entry()
    if request.method == 'POST':
        UploadLinks(form.list.data, cams)
        return 'We confirm your registration!'
    return render_template('customization/camera_registration.html', form=form)


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


if __name__ == "__main__":
    app.jinja_env.globals.update(_build_auth_url=_build_auth_url)
    app.run(host='0.0.0.0', threaded=True)
