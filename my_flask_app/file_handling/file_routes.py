""" Filename: file_routes.py - Directory: my_flask_app/file_handling
"""
import os
import traceback
import boto3
import logging
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
    send_file,
)
from flask_login import current_user
from werkzeug.utils import secure_filename
from database.models import db, FileUpload
from utils.docx_utils import correct_text_grammar
from utils.exceptions import GrammarCheckError
from botocore.exceptions import NoCredentialsError

file_blueprint = Blueprint("file_blueprint", __name__)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Adjust the log level as needed (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s [%(levelname)s] - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),  # Log to a file (optional)
        logging.StreamHandler(),  # Log to console
    ],
)


def get_s3_client():
    """
    Initialize and return a boto3 S3 client using current app configuration.
    """
    return boto3.client(
        "s3",
        region_name="us-east-1",
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
    # Check if file is part of the request
    if "file" not in request.files:
        flash("No file part", "error")
        print("No file part in request")
        return redirect(url_for("index"))

    file = request.files["file"]

    # Check if file has a filename
    if file.filename == "":
        flash("No selected file", "error")
        print("No selected file")
        return redirect(url_for("index"))

    # Secure the filename and upload the file to S3
    filename = secure_filename(file.filename)
    print(f"Received file: {filename}")

    try:
        file_url = upload_file_to_s3(file, current_app.config["S3_BUCKET"])
        print(f"File uploaded to S3: {file_url}")
    except Exception as e:
        flash("Error uploading file to S3", "error")
        print(f"Error uploading file to S3: {e}")
        return redirect(url_for("file_blueprint.index"))

    # Process the file and store corrections
    try:
        print("Starting grammar correction")
        corrections = await correct_text_grammar(file_url)
        flash("Content checked successfully.", "success")
        print("Grammar correction completed")
    except IOError as io_error:
        flash(f"File I/O error: {str(io_error)}", "error")
        print(f"File I/O error: {io_error}")
        return redirect(url_for("file_blueprint.index"))
    except ValueError as value_error:
        flash(f"Value error: {str(value_error)}", "error")
        print(f"Value error: {value_error}")
        return redirect(url_for("file_blueprint.index"))
    except GrammarCheckError as grammar_error:
        flash(f"Grammar check error: {str(grammar_error)}", "error")
        print(f"Grammar check error: {grammar_error}")
        return redirect(url_for("file_blueprint.index"))

    # Update or create file upload record
    try:
        existing_file = FileUpload.query.filter_by(file_name=filename).first()
        if existing_file:
            existing_file.corrections = corrections
            db.session.commit()
            session["file_id"] = existing_file.id
            print(f"Updated existing file record: {filename}")
        else:
            new_file = FileUpload(
                file_name=filename, file_path=file_url, corrections=corrections
            )
            db.session.add(new_file)
            db.session.commit()
            session["file_id"] = new_file.id
            print(f"Created new file record: {filename}")
    except Exception as e:
        flash("Error updating database", "error")
        print(f"Error updating database: {e}")
        return redirect(url_for("file_blueprint.index"))

    return redirect(url_for("file_blueprint.index"))


@file_blueprint.route("/download/<int:file_id>")
def download_file(file_id):
    file = FileUpload.query.get_or_404(file_id)

    # Generate a presigned URL for the S3 object
    s3_client = get_s3_client()
    try:
        presigned_url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": current_app.config["S3_BUCKET"], "Key": file.file_name},
            ExpiresIn=300,
        )  # URL expires in 5 minutes
        print(f"File {file.file_name} downloaded ")

    except NoCredentialsError:
        flash("Error generating presigned URL for download", "error")
        print("Error generating presigned URL for download")

        return redirect(url_for("file_blueprint.index"))

    # Redirect user to the presigned URL
    return redirect(presigned_url)


@file_blueprint.route("/delete/<int:file_id>")
def delete_file(file_id):
    s3 = get_s3_client()  # Initialize the S3 client
    file = FileUpload.query.get_or_404(file_id)

    try:
        s3.delete_object(Bucket=current_app.config["S3_BUCKET"], Key=file.file_name)
        db.session.delete(file)
        db.session.commit()
        flash(f"{file.file_name} was deleted successfully", "success")
        print(f"File {file.file_name} deleted")

        # Log success message
        logging.info(f"File {file.file_name} deleted successfully")

    except Exception as e:
        flash(f"Error deleting file from S3: {str(e)}", "error")
        print(f"Error deleting file from S3: {str(e)}")

        # Log the error message and stack trace
        logging.error(f"Error deleting file from S3: {str(e)}", exc_info=True)

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
