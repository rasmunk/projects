import os
from configparser import SafeConfigParser
from projects import app

config = SafeConfigParser()
config.read(os.path.abspath("projects_base/res/config.ini"))
config.read(os.path.abspath("res/config.ini"))
# Required folders
folders = {}
folders['DATA_FOLDER'] = app.config['DATA_FOLDER'] \
    = os.path.abspath(config.get('PROJECTS', 'data_folder'))
folders['UPLOAD_FOLDER'] = app.config['UPLOAD_FOLDER'] \
    = os.path.abspath(config.get('PROJECTS', 'upload_folder'))

# Create required folders for the application if they don't exist
for key, folder in folders.items():
    try:
        os.makedirs(folder)
        print("Created: " + folder)
    except FileExistsError:
        pass

# Db lockfile
app.config['DB_LOCK'] = os.path.join(
    os.path.abspath(config.get('PROJECTS', 'data_folder')), 'projects_db_lock')

# Default db target
app.config['DB'] = os.path.join(
    os.path.abspath(config.get('PROJECTS', 'data_folder')), "projects_dev")

# Onetime authentication reset token salt
app.config['ONETIME_TOKEN_SALT'] = os.urandom(24)

# Projects static folder
app.config['PROJECTS_STATIC_FOLDER'] = os.path.abspath(
    config.get('PROJECTS', 'static_folder'))

# Application ADMINS_EMAIL
app.config['ADMINS_EMAIL'] = config.get('MAIL', 'admins')

# Email application server
app.config['MAIL_SERVER'] = config.get('MAIL', 'server')
app.config['MAIL_PORT'] = config.get('MAIL', 'port')
app.config['MAIL_USE_TLS'] = bool(config.get('MAIL', 'use_tls'))
app.config['MAIL_USE_SSL'] = bool(config.get('MAIL', 'use_ssl'))
app.config['MAIL_USERNAME'] = config.get('MAIL', 'username')
app.config['MAIL_PASSWORD'] = config.get('MAIL', 'password')

# Config
app.config['TITLE'] = config.get('PROJECTS', 'title')
