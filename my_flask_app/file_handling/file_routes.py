""" Filename: file_routes.py - Directory: my_flask_app/file_handling

This module defines routes for file upload, download, deletion, and correction retrieval
in a Flask web application. It provides functionality to upload files, check their
content for grammar corrections, download files, delete files, and retrieve
correction details.

"""
import pytz
import os
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
from datetime import datetime
import os

file_blueprint = Blueprint("file_blueprint", __name__)
    
@file_blueprint.route("/upload", methods=["POST"])
def upload_file():
    """Upload a file and check its content for grammar corrections.
    Returns:
        redirect: Redirects to the index page after processing the file.
    """
 
    upload_limits = {
        "Free": 10,
        "Basic": 50,
        "Premium": 100
    }
    
    # Convert current UTC time to Vietnam time
    vn_timezone = pytz.timezone('Asia/Ho_Chi_Minh')
    current_time_vn = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(vn_timezone)
    current_date_vn = current_time_vn.date() # Extract the date part


    # Check if it's a new day in Vietnam time
    if current_user.last_upload_date is None or current_user.last_upload_date.date() < current_date_vn:
        current_user.daily_upload_count = 0
        db.session.commit()

    # Get the upload limit for the current user's account type
    upload_limit_per_day = upload_limits.get(current_user.account_type, 1)  # Default to 1 if account type is not in the dictionary

    # Check if the user has reached the upload limit for the day
    if current_user.daily_upload_count >= upload_limit_per_day:
        flash("Daily upload limit reached. Please try again tomorrow.", "warning")
        return redirect(url_for("index"))

    # Process the file upload
    # ...

    # Increment the upload count and update the last upload date (in Vietnam time)
    current_user.daily_upload_count += 1
    current_user.last_upload_date = current_time_vn
    db.session.commit()
    
    # Print the file size
    file_size = request.content_length
    file_size_MB = file_size / (1024.0 * 1024.0)
    flash(f"Uploaded file size: {file_size_MB} Megabytes (MB)", "success") 
    # Map account types to their file size limits (in bytes)
    size_limits = {
        "Free": 1,  # 1 MB
        "Basic": 10, # 10 MB
        "Premium": 20 # 20 MB
    }

    # Get the file size limit for the current user's account type
    max_size = size_limits.get(current_user.account_type, None)

    # If account type is not recognized, default to smallest size limit (1 MB)
    if max_size is None:
        max_size = size_limits["Free"]

    # Check if the file size exceeds the limit
    if file_size_MB > max_size:
        flash(f"{current_user.account_type} accounts can only upload files up to {max_size} MB.", "warning")
        return redirect(url_for("index"))
    
    if "file" not in request.files:
        flash("No file part", "error")
        return redirect(url_for("index"))
    file = request.files["file"]

    if file.filename == "":
        flash("No selected file", "error")
        return redirect(url_for("index"))

    filename = secure_filename(file.filename)
    file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    file.save(file_path)

    # Process the file and store corrections
    try:
        corrections = correct_text_grammar(file_path)
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
        existing_file.upload_time = datetime.now()
        existing_file.corrections = corrections
        db.session.commit()
        session["file_id"] = existing_file.id  # Use the existing file's ID
        
    else:
        new_file = FileUpload(
            file_name=filename, file_path=file_path, corrections=corrections, upload_time=datetime.now()
        )
        db.session.add(new_file)
        db.session.commit()
        session["file_id"] = new_file.id  # Use the existing file's ID
        
    return redirect(url_for("file_blueprint.index"))



@file_blueprint.route("/download/<int:file_id>")
def download_file(file_id):
    """
    Download a file with the specified file_id.
    Args:
        file_id (int): The ID of the file to be downloaded.
    Returns:
        Response: A response containing the file to be downloaded.
    """
    file = FileUpload.query.get_or_404(file_id)
    return send_from_directory(
        current_app.config["UPLOAD_FOLDER"], file.file_name, as_attachment=True
    )


@file_blueprint.route("/delete/<int:file_id>")
def delete_file(file_id):
    """Delete a file with the specified file_id.
    Args:
        file_id (int): The ID of the file to be deleted.
    Returns:
        redirect: Redirects to the index page after deleting the file.
    """
    file_to_delete = FileUpload.query.get_or_404(file_id)
    try:
        os.remove(
            os.path.join(current_app.config["UPLOAD_FOLDER"], file_to_delete.file_name)
        )
        db.session.delete(file_to_delete)
        db.session.commit()
        flash(f"{file_to_delete.file_name} was deleted successfully", "success")
    except OSError as e:
        flash(f"Error deleting file from filesystem: {str(e)}", "error")
    return redirect(url_for("file_blueprint.index"))


@file_blueprint.route("/corrections/<int:file_id>")
def get_corrections(file_id):
    """Get corrections for a file with the specified file_id.
    Args:
        file_id (int): The ID of the file to retrieve corrections for.
    Returns:
        jsonify: JSON response containing the corrections for the file.
    """
    file = FileUpload.query.get_or_404(file_id)
    corrections = file.corrections
    files = FileUpload.query.all()  # Fetch all files to display on the index page

    return render_template(
        "index.html", files=files, corrections=corrections, current_user=current_user
    )


@file_blueprint.route("/")
def index():
    """
    Fetches uploaded files and their grammar corrections, if available,
    from the database and renders them on the homepage.
    Returns:
        str: Rendered HTML content for the homepage.
    """
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
