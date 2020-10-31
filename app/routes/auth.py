from flask import redirect, render_template, request, session, url_for
import routes.helpers.auth as authHelpers
import app_config
import requests
import uuid
import msal


def login():
    session["state"] = str(uuid.uuid4())
    # Technically we could use empty list [] as scopes to do just sign in,
    # here we choose to also collect end user consent upfront
    auth_url = authHelpers._build_auth_url(scopes=app_config.SCOPE, state=session["state"])
    return render_template("auth/login.html", auth_url=auth_url, version=msal.__version__)


def authorized():
    if request.args.get('state') != session.get("state"):
        return redirect(url_for("index"))  # No-OP. Goes back to Index page
    if "error" in request.args:  # Authentication/Authorization failure
        return render_template("auth/auth_error.html", result=request.args)
    if request.args.get('code'):
        cache = authHelpers._load_cache()
        result = authHelpers._build_msal_app(cache=cache).acquire_token_by_authorization_code(
            request.args['code'],
            scopes=app_config.SCOPE,  # Misspelled scope would cause an HTTP 400 error here
            redirect_uri=url_for("authorized", _external=True))
        if "error" in result:
            return render_template("auth/auth_error.html", result=result)
        session["user"] = result.get("id_token_claims")
        authHelpers._save_cache(cache)
    return redirect(url_for("index"))


def logout():
    session.clear()  # Wipe out user and its token cache from session
    return redirect(  # Also logout from your tenant's web session
        app_config.AUTHORITY + "/oauth2/v2.0/logout" +
        "?post_logout_redirect_uri=" + url_for("index", _external=True))


def graphcall():
    token = authHelpers._get_token_from_cache(app_config.SCOPE)
    if not token:
        return redirect(url_for("login"))
    graph_data = requests.get(  # Use token to call downstream service
        app_config.ENDPOINT,
        headers={'Authorization': 'Bearer ' + token['access_token']},
    ).json()
    return render_template('auth/display.html', result=graph_data)
