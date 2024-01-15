import sys
import site

# Activate your virtual environment
activate_this = '/home/ec2-user/doc_grammar/venv/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

# Add your site-packages and the app directory to the path
site.addsitedir('/home/ec2-user/doc_grammar/venv/lib/python3.11/site-packages')
sys.path.insert(0, '/home/ec2-user/doc_grammar/my_flask_app')

from app import app as application
