import sys

# Add the app directory to the path
sys.path.insert(0, '/home/ec2-user/my_flask_app/my_flask_app')

from app import app as application
