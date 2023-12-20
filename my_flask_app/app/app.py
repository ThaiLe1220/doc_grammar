""" Filename: app.py - Directory: my_flask_app 
"""
import os
from flask import (
    Flask,
    render_template,
    session,
)
from flask_login import current_user
from file_handling.file_routes import file_blueprint
from my_flask_app.database.db_setup import setup_database
from my_flask_app.database.models import FileUpload

app = Flask(__name__, template_folder="/app/templates")

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URI")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

if not os.path.exists("file_uploads"):
    os.makedirs("file_uploads")

app.config["UPLOAD_FOLDER"] = "file_uploads"

setup_database(app)

# Register blueprints
app.register_blueprint(file_blueprint, url_prefix="/files")


@app.route("/")
def index():
    files = FileUpload.query.all()
    file_id = session.get("file_id")
    corrections = None

    if file_id:
        file = FileUpload.query.get(file_id)
        if file:
            corrections = file.corrections

    return render_template(
        "index.html", files=files, corrections=corrections, current_user=current_user
    )


if __name__ == "__main__":
    app.run(debug=True)
