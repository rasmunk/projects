import os
import jinja2
import datetime
from bcrypt import hashpw, gensalt
from flask_wtf.csrf import CSRFProtect
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_mail import Mail
from projects_base.base import app
from projects.models import User
from projects.forms import ProjectFormManager, DefaultProjectForm


# Load multiple shared_templates paths
all_temp = [os.path.abspath("projects/templates"),
            os.path.join(app.root_path, "/templates")]
custom_loader = jinja2.ChoiceLoader([app.jinja_loader,
                                     jinja2.FileSystemLoader(all_temp)])
app.jinja_loader = custom_loader

csrf = CSRFProtect(app)
app.secret_key = os.urandom(24)
Bootstrap(app)

# Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

import projects.conf
from projects.conf import config
# Connect mail
mail = Mail(app)

project_manager = ProjectFormManager()
project_manager.register_form_class(config.get('PROJECTS', 'form_class'),
                                    config.get('PROJECTS', 'form_module',
                                               **{'fallback': None}))

# Setup projects config statics
import projects.nav
import projects.views

# If debug option
if app.debug:
    # Implement test user
    user = User.get_with_first('email', 'test@nbi.ku.dk')
    if user is None:
        user = User(email='test@nbi.ku.dk',
                    password=hashpw(bytes("test", 'utf-8'),
                                    gensalt()),
                    projects=[], is_active=True,
                    is_authenticated=True, is_anonymous=False,
                    confirmed_on=datetime.datetime.now())
        user.save()

