# soundtrack.wsgi - WSGI entry point for Apache + mod_wsgi

import sys
import os

# Add your project directory to Python path
# Change this to the actual path of your project
project_home = '/var/www/SoundTrack'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Activate your virtual environment (if using one)
# Change this to the path of your venv's activate_this.py
activate_this = '/var/www/SoundTrack/venv/bin/Activate.ps1'
if os.path.exists(activate_this):
    with open(activate_this) as file_:
        exec(file_.read(), dict(__file__=activate_this))

# Change directory to project home (so relative paths work)
os.chdir(project_home)

# Import your Flask app
from app import app as application

