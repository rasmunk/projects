# Common configuration
import os
import configparser
from projects_base.base import app

# Load config.ini
res_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                        '..', 'res', 'config.ini')
config = configparser.SafeConfigParser()
config.read(res_path)

# common static folder path
app.config['STATIC_FOLDER'] = os.path.abspath(config.get('BASE',
                                                         'static_folder'))
app.config['UPLOAD_FOLDER'] = os.path.abspath(config.get('BASE',
                                                         'upload_folder'))
