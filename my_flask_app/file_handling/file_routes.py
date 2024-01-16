""" Filename: file_routes.py - Directory: my_flask_app/file_handling
"""
import os
import traceback
import boto3
from flask import (
    Blueprint,
    render_template,
    send_from_directory,
    redirect,
    url_for,
    flash,
    request,
    current_app,
    session,
)
from flask_login import current_user
from werkzeug.utils import secure_filename
from database.models import db, FileUpload
from utils.docx_utils import correct_text_grammar
from utils.exceptions import GrammarCheckError

file_blueprint = Blueprint("file_blueprint", __name__)


def get_s3_client():
    """
    Initialize and return a boto3 S3 client using current app configuration.
    """
    return boto3.client(
        "s3",
        aws_access_key_id=current_app.config["S3_KEY"],
        aws_secret_access_key=current_app.config["S3_SECRET"],
    )


def upload_file_to_s3(file, bucket_name):
    s3 = get_s3_client()  # Initialize the S3 client
    try:
        s3.upload_fileobj(
            file,
            bucket_name,
            file.filename,
            ExtraArgs={"ContentType": file.content_type},
        )
        file_url = f"{current_app.config['S3_LOCATION']}{file.filename}"
        return file_url
    except Exception as e:
        print("Something Happened: ", e)
        traceback.print_exc()  # Print the stack trace
        return None


@file_blueprint.route("/upload", methods=["POST"])
async def upload_file():
    if "file" not in request.files:
        flash("No file part", "error")
        return redirect(url_for("index"))
    file = request.files["file"]

    if file.filename == "":
        flash("No selected file", "error")
        return redirect(url_for("index"))

    filename = secure_filename(file.filename)
    file_url = upload_file_to_s3(file, current_app.config["S3_BUCKET"])
    print(file_url)

    # Process the file and store corrections
    try:
        corrections = await correct_text_grammar(file_url)
        flash("Content checked successfully.", "success")

    except IOError as io_error:
        flash(f"File I/O error: {str(io_error)}", "error")
        return redirect(url_for("file_blueprint.index"))
    except ValueError as value_error:
        flash(f"Value error: {str(value_error)}", "error")
        return redirect(url_for("file_blueprint.index"))
    except GrammarCheckError as grammar_error:
        flash(f"Grammar check error: {str(grammar_error)}", "error")
        return redirect(url_for("file_blueprint.index"))

    # Update or create file upload record
    existing_file = FileUpload.query.filter_by(file_name=filename).first()
    if existing_file:
        existing_file.corrections = corrections
        db.session.commit()
        session["file_id"] = existing_file.id  # Use the existing file's ID

    else:
        new_file = FileUpload(
            file_name=filename, file_path=file_url, corrections=corrections
        )
        db.session.add(new_file)
        db.session.commit()
        session["file_id"] = new_file.id  # Use the existing file's ID

    return redirect(url_for("file_blueprint.index"))


@file_blueprint.route("/download/<int:file_id>")
def download_file(file_id):
    file = FileUpload.query.get_or_404(file_id)
    return redirect(file.file_path)


@file_blueprint.route("/delete/<int:file_id>")
def delete_file(file_id):
    s3 = get_s3_client()  # Initialize the S3 client
    file_to_delete = FileUpload.query.get_or_404(file_id)
    try:
        s3.delete_object(
            Bucket=current_app.config["S3_BUCKET"], Key=file_to_delete.file_name
        )
        db.session.delete(file_to_delete)
        db.session.commit()
        flash(f"{file_to_delete.file_name} was deleted successfully", "success")
    except Exception as e:
        flash(f"Error deleting file from S3: {str(e)}", "error")
    return redirect(url_for("file_blueprint.index"))


@file_blueprint.route("/corrections/<int:file_id>")
def get_corrections(file_id):
    file = FileUpload.query.get_or_404(file_id)
    corrections = file.corrections
    files = FileUpload.query.all()  # Fetch all files to display on the index page

    return render_template(
        "index.html", files=files, corrections=corrections, current_user=current_user
    )


@file_blueprint.route("/")
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
