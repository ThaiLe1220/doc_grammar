import logging
from flask import Flask

app = Flask(__name__)

# Set up logging
logging.basicConfig(filename='myapp.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')

# Your Flask app code here...

import sys
import site

# Activate your virtual environment
activate_this = '/home/ec2-user/my_flask_app/venv/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

# Add your site-packages and the app directory to the path
site.addsitedir('/home/ec2-user/my_flask_app/venv/lib/python3.9/site-packages')
sys.path.insert(0, '/home/ec2-user/my_flask_app/my_flask_app')

from app import app as application
