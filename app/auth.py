# -*- encoding=utf-8 -*-
# Inspired from the tutorial by Microsoft form azure active directory authentication
# Tutorial Source: https://github.com/rebremer/ms-identity-python-webapp-backend
import msal
import uuid
import config
import functools
from flask import redirect, request, session, url_for


def login_required(f):
    """
    index route
    :param:
    :return: 
    """
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        """
        index route
        :param:
        :return: 
        """
        if not session.get("user"):
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def _load_cache():
    """
    index route
    :param:
    :return: 
    """
    cache = msal.SerializableTokenCache()
    if session.get("token_cache"):
        cache.deserialize(session["token_cache"])
    return cache


def _save_cache(cache):
    """
    index route
    :param:
    :return: 
    """
    if cache.has_state_changed:
        session["token_cache"] = cache.serialize()


def _build_msal_app(cache=None, authority=None):
    """
    index route
    :param:
    :return: 
    """
    return msal.ConfidentialClientApplication(
        config.CLIENT_ID, 
        authority=authority or config.AUTHORITY,
        client_credential=config.CLIENT_SECRET, 
        token_cache=cache
        )


def _build_auth_url(authority=None, scopes=None, state=None):
    """
    index route
    :param:
    :return: 
    """
    return _build_msal_app(authority=authority).get_authorization_request_url(
        scopes or [],
        state=state or str(uuid.uuid4()),
        redirect_uri=url_for("authorized", _external=True)
        )


def _get_token_from_cache(scope=None):
    """
    index route
    :param:
    :return: 
    """
    # This web app maintains one cache per session
    cache = _load_cache()
    cca = _build_msal_app(cache=cache)
    accounts = cca.get_accounts()
    # So all account(s) belong to the current signed-in user
    if accounts:
        result = cca.acquire_token_silent(scope, account=accounts[0])
        _save_cache(cache)
        return result
