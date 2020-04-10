import os
from flask import Flask, Blueprint
from flask_wtf.csrf import CSRFProtect
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_mail import Mail
from flask_nav import Nav
from projects_base.base import base_blueprint
from projects.models import User
from projects.forms import ProjectFormManager, DefaultProjectForm
from projects.conf import config

app = Flask(__name__)
app.register_blueprint(base_blueprint)
projects_blueprint = Blueprint(
    "projects",
    __name__,
    static_folder="static",
    static_url_path="/projects/static",
    template_folder="templates",
)

csrf = CSRFProtect(app)
app.secret_key = os.urandom(24)
Bootstrap(app)

# Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "projects.login"

project_manager = ProjectFormManager()

# Onetime authentication reset token salt
app.config["ONETIME_TOKEN_SALT"] = os.urandom(24)

# TODO -> fix hack at some point
# Application ADMINS_EMAIL
if "ADMINS_EMAIL" in os.environ:
    app.config["ADMINS_EMAIL"] = os.environ["ADMINS_EMAIL"].split(",")
else:
    app.config["ADMINS_EMAIL"] = config.get("MAIL", "admins")

# Email application server
if "MAIL_SERVER" in os.environ:
    app.config["MAIL_SERVER"] = os.environ["MAIL_SERVER"]
else:
    app.config["MAIL_SERVER"] = config.get("MAIL", "server")

if "MAIL_PORT" in os.environ:
    app.config["MAIL_PORT"] = os.environ["MAIL_PORT"]
else:
    app.config["MAIL_PORT"] = config.get("MAIL", "port")

if "MAIL_USE_TLS" in os.environ:
    app.config["MAIL_USE_TLS"] = bool(os.environ["MAIL_USE_TLS"])
else:
    # NOTE!, remember that if any value is set for use_tls it is set to True
    app.config["MAIL_USE_TLS"] = bool(config.get("MAIL", "use_tls"))

if "MAIL_USE_SSL" in os.environ:
    app.config["MAIL_USE_SSL"] = (
        False if os.environ["MAIL_USE_SSL"] == "False" else True
    )
else:
    # NOTE!, remember that if any value is set for use_ssl it is set to True
    app.config["MAIL_USE_SSL"] = bool(config.get("MAIL", "use_ssl"))

if "MAIL_USERNAME" in os.environ:
    app.config["MAIL_USERNAME"] = os.environ["MAIL_USERNAME"]
else:
    app.config["MAIL_USERNAME"] = config.get("MAIL", "username")

if "MAIL_PASSWORD" in os.environ:
    app.config["MAIL_PASSWORD"] = os.environ["MAIL_PASSWORD"]
else:
    app.config["MAIL_PASSWORD"] = config.get("MAIL", "password")

# Connect mail
mail = Mail(app)

# Setup navbar
nav = Nav()
nav.init_app(app)
import projects.nav
import projects.views

app.register_blueprint(projects_blueprint)
