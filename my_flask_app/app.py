# Filename: app.py - Directory: my_flask_app
from flask import (
    Flask,
    render_template,
    request,
    send_from_directory,
    redirect,
    url_for,
    flash,
    jsonify,
    session,
)
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
import os
from utils.docx_utils import correct_text_grammar
from sqlalchemy.dialects.postgresql import JSONB


app = Flask(__name__)

app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql://eugene:eugene@localhost/doc_grammar"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # To suppress a warning
app.config["SECRET_KEY"] = "eugene_secret"  # Needed for flashing messages

db = SQLAlchemy(app)

if not os.path.exists("file_uploads"):
    os.makedirs("file_uploads")

app.config["UPLOAD_FOLDER"] = "file_uploads"


# Define a FileUpload class as the ORM model
class FileUpload(db.Model):
    __tablename__ = "file_uploads"
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(255), nullable=False, unique=True)
    file_path = db.Column(db.Text, nullable=False)
    upload_time = db.Column(db.DateTime, server_default=db.func.now())
    corrections = db.Column(JSONB)


@app.route("/check_db")
def check_database_connection():
    try:
        db.session.query(FileUpload).first()
        return "Database connection successful. Happy coding"
    except Exception as e:
        return f"Database connection error: {str(e)}"


@app.route("/")
def index():
    files = FileUpload.query.all()
    file_id = session.get("file_id")
    corrections = None

    if file_id:
        file = FileUpload.query.get(file_id)
        if file:
            corrections = file.corrections

    return render_template("index.html", files=files, corrections=corrections)


# Route for file upload and listing
@app.route("/", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        flash("No file part", "error")
        return redirect(url_for("index"))
    file = request.files["file"]
    if file.filename == "":
        flash("No selected file", "error")
        return redirect(url_for("index"))
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    # Determine if it's an existing file
    existing_file = FileUpload.query.filter_by(file_name=filename).first()

    # Save or overwrite the file
    file.save(file_path)

    # After saving, replace the text
    try:
        # Process the file and get corrections
        corrections = correct_text_grammar(file_path)
        flash("Content checked successfully.", "success")
    except Exception as e:
        flash(f"Error replacing content: {str(e)}", "error")

    # Update the database record if it exists, otherwise create a new one
    if existing_file:
        existing_file.corrections = corrections
        flash(f"{filename} was updated successfully", "success")
    else:
        new_upload = FileUpload(
            file_name=filename, file_path=file_path, corrections=corrections
        )
        db.session.add(new_upload)
        flash("File uploaded successfully", "success")

    db.session.commit()

    if corrections:
        session["file_id"] = new_upload.id  # Save the file id in the session

        files = FileUpload.query.all()  # Refresh the file list
        return render_template(
            "index.html", files=files, corrections=corrections
        )  # Pass the corrections to the template.

    # If there are no corrections or if you need to redirect for some other reason:
    return redirect(url_for("index"))


# File downloading route
@app.route("/download/<int:file_id>")
def download_file(file_id):
    file = FileUpload.query.get_or_404(file_id)
    return send_from_directory(
        app.config["UPLOAD_FOLDER"], file.file_name, as_attachment=True
    )


@app.route("/corrections/<int:file_id>")
def get_corrections(file_id):
    file = FileUpload.query.get_or_404(file_id)
    corrections = file.corrections
    # You can either send this data back as JSON or render it in an HTML template
    return jsonify(corrections)  # For AJAX requests
    # return render_template("corrections.html", corrections=corrections)  # For server-side rendering


# File deleting route
@app.route("/delete/<int:file_id>")
def delete_file(file_id):
    file_to_delete = FileUpload.query.get_or_404(file_id)

    # Attempt to delete the file from the filesystem
    try:
        os.remove(os.path.join(app.config["UPLOAD_FOLDER"], file_to_delete.file_name))
    except OSError as e:
        flash(f"Error deleting file from filesystem: {str(e)}", "error")
        return redirect(url_for("upload_file"))

    # Delete the record from the database
    db.session.delete(file_to_delete)
    db.session.commit()

    flash(f"{file_to_delete.file_name} was deleted successfully", "success")
    return redirect(url_for("upload_file"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensure all tables are created
    app.run(debug=True)
