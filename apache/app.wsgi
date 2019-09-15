#!/usr/bin/python3
import os
# Load environment variables
exec(open(os.path.join(os.environ['ENV_DIR'], 'projects-envvars.py')).read())
from projects import app as application
