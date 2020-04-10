# http://flask.pocoo.org/snippets/62/
import base64
from os import urandom
from urllib.parse import urlparse, urljoin
from flask import request
from itsdangerous import URLSafeTimedSerializer, BadSignature
from projects import app
from projects import login_manager
from projects.models import User


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc


# LoginManager
@login_manager.user_loader
def load_user(user_id):
    user = User.get(user_id)
    return user


def generate_confirmation_token(data):
    serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])
    return serializer.dumps(data, salt=app.config["ONETIME_TOKEN_SALT"])


# A token is valid for a day
def confirm_token(token, expiration=86400):
    serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])
    try:
        data = serializer.loads(
            token, salt=app.config["ONETIME_TOKEN_SALT"], max_age=expiration
        )
    except BadSignature:
        return False
    return data


def unique_name_encoding(name):
    """
    :param name: raw string name
    :return: the raw string name is padded with a 10 byte urandom string
    extension
    """
    assert type(name) == str
    return name + "_" + str(base64.b64encode(urandom(10)))


def unique_name_decode(name):
    """
    :param name: encoded name
    :return:
    """
    assert type(name) == str
    idx = name.rfind("_")
    return name[:idx]
