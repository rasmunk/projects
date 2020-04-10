#!/usr/bin/python3
import os
if 'PROJECTS_ENV_DIR' in os.environ:
    path = os.path.join(os.environ['PROJECTS_ENV_DIR'], 'envvars.py')
    if os.path.exists(path):
        exec(open(path).read())
from projects import app as application
