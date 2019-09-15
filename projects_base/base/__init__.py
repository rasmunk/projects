from flask import Flask
app = Flask(__name__)

# Load common configuration
import projects_base.base.conf
import projects_base.base.views
