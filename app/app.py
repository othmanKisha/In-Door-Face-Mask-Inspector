import auth
import uuid
import config
import requests
from flask_session import Session
from camera import Camera, generate
import flask_monitoringdashboard as dashboard
from werkzeug.middleware.proxy_fix import ProxyFix
from flask import Flask, flash, redirect, render_template, request, Response, session, url_for
                   

app = Flask(__name__)
app.config.from_object(config)
dashboard.bind(app)
Session(app)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
app.jinja_env.globals.update(_build_auth_url=auth._build_auth_url)

cameras_collection = config.db['cameras']
security_collection = config.db['security']


@app.route("/", methods=['GET'])
@auth.login_required
def index():
    """
    index route
    :param:
    :return: home template which takes the list of all security members in addition
             the list of all cameras where it also receives the first and last name
             of the camera supervisor.
    """
    args = []
    camera = cameras_collection.find({})
    security = security_collection.find({})
    for cam in camera:
        name = ""
        for sec in security:
            if sec["_id"] == cam["supervisor_id"]:
                name = f"{sec['first_name']} {sec['last_name']}"
                break
        args.append({
            "_id": cam["_id"],
            "location": cam["location"],
            "status": cam["status"],
            "url": cam["url"],
            "security_member": name,
            "supervisor_id": cam['supervisor_id']
        })
    return render_template('pages/home.html', 
                            args=args, 
                            security=security
                            )


@app.route("/create_camera", methods=['POST'])
@auth.login_required
def create_camera():
    """
    index route
    :param:
    :return: 
    """
    _id = uuid.uuid4()
    data = request.form.copy()
    try:
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


@app.route("/create_security", methods=['POST'])
@auth.login_required
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
        flash(f"success|Security member {data.get('first_name')} {data.get('last_name')} has been successfully added.")
    except:
        flash(f"danger|Security member couldn't be added")
    finally:
        return redirect(url_for("index"))


@app.route("/edit_camera/<uuid:id>", methods=['POST'])
@auth.login_required
def edit_camera(id):
    """
    index route
    :param:
    :return: 
    """
    data = request.form.copy()
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


@app.route("/edit_security/<uuid:id>", methods=['POST'])
@auth.login_required
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


@app.route("/delete_camera/<uuid:id>", methods=['POST'])
@auth.login_required
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


@app.route("/delete_security/<uuid:id>", methods=['POST'])
@auth.login_required
def delete_security(id):
    """
    index route
    :param:
    :return: 
    """
    try:
        security_collection.delete_one({"_id": id})
        flash(f"success|Security member has been successfully deleted.")
    except:
        flash(f"danger|Security member couldn't be deleted")
    finally:
        return redirect(url_for("index"))


@app.route('/video_feed/<uuid:id>')
@auth.login_required
def video_feed(id):
    """
    index route
    :param:
    :return: 
    """
    try:
        cam = cameras_collection.find_one({'_id': id})
        return Response(generate(Camera(cam['url'])),
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
    auth_url = auth._build_auth_url(
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
        cache = auth._load_cache()
        result = auth._build_msal_app(cache=cache).acquire_token_by_authorization_code(
            request.args['code'],
            # Misspelled scope would cause an HTTP 400 error here
            scopes=config.SCOPE,
            redirect_uri=url_for("authorized", _external=True)
            )
        if "error" in result:
            return render_template("auth_error.html", result=result)
        session["user"] = result.get("id_token_claims")
        auth._save_cache(cache)
    return redirect(url_for("index"))


if __name__ == "__main__":
    # Run the server
    app.run(host='0.0.0.0', threaded=True)
