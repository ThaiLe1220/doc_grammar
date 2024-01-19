""" Filename: file_routes.py - Directory: my_flask_app/file_handling
"""

import time
import pytz
import os
import tempfile

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
from flask_login import login_required
from werkzeug.utils import secure_filename
from database.models import db, FileUpload
from utils.docx_utils import correct_text_grammar
from utils.exceptions import GrammarCheckError
from datetime import datetime
from zipfile import ZipFile

file_blueprint = Blueprint("file_blueprint", __name__)


@file_blueprint.route("/upload", methods=["POST"])
@login_required
async def upload_file():
    start_time = datetime.now()
    upload_limits = {"Free": 10, "Basic": 50, "Premium": 100}
    # Convert current UTC time to Vietnam time
    vn_timezone = pytz.timezone("Asia/Ho_Chi_Minh")
    current_time_vn = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(vn_timezone)
    current_date_vn = current_time_vn.date()  # Extract the date part

    # Check if it's a new day in Vietnam time
    if (
        current_user.last_upload_date is None
        or current_user.last_upload_date.date() < current_date_vn
    ):
        current_user.daily_upload_count = 0
        db.session.commit()

    # Get the upload limit for the current user's account type
    upload_limit_per_day = upload_limits.get(
        current_user.account_type, 10
    )  # Default to 10 if account type is not in the dictionary

    # Check if the user has reached the upload limit for the day
    if current_user.daily_upload_count >= upload_limit_per_day:
        flash("Daily upload limit reached. Please try again tomorrow.", "warning")
        return redirect(url_for("index"))

    # Increment the upload count and update the last upload date (in Vietnam time)
    current_user.daily_upload_count += 1
    current_user.last_upload_date = current_time_vn
    db.session.commit()

    # Print the file size
    file_size = request.content_length
    file_size_MB = file_size / (1024.0 * 1024.0)
    formatted_size = f"{file_size_MB:.2f}"
    flash(f"Uploaded file size: {formatted_size} Megabytes (MB)", "success")
    # Map account types to their file size limits (in bytes)
    size_limits = {"Free": 1, "Basic": 2, "Premium": 20}  # 1 MB  # 10 MB  # 20 MB

    # Get the file size limit for the current user's account type
    max_size = size_limits.get(current_user.account_type, None)

    # If account type is not recognized, default to smallest size limit (1 MB)
    if max_size is None:
        max_size = size_limits["Free"]

    # Check if the file size exceeds the limit
    if file_size_MB > max_size:
        current_user.daily_upload_count -= 1
        db.session.commit()
        flash(
            f"{current_user.account_type} accounts can only upload files up to {max_size} MB.",
            "warning",
        )
        return redirect(url_for("index"))

    if "file" not in request.files:
        current_user.daily_upload_count -= 1
        db.session.commit()
        flash("No file part", "error")
        return redirect(url_for("index"))
    file = request.files["file"]

    if file.filename == "":
        current_user.daily_upload_count -= 1
        db.session.commit()
        flash("No selected file", "error")
        return redirect(url_for("index"))

    filename = secure_filename(file.filename)
    timestamp = int(time.time())  # Current time as an integer timestamp
    unique_filename = f"{timestamp}_{filename}"
    file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], unique_filename)
    file.save(file_path)
    print(f"Received file: {unique_filename}")

    # Process the file and store corrections
    try:
        print("Starting grammar correction")
        corrections = await correct_text_grammar(file_path)
        end_time = datetime.now()
        processing_duration = end_time - start_time
        flash(
            f"Content checked successfully in {processing_duration.total_seconds()} seconds.",
            "success",
        )
        print("Grammar correction completed")

    except IOError as io_error:
        flash(f"File I/O error: {str(io_error)}", "error")
        print(f"File I/O error: {io_error}")
        return redirect(url_for("index", page=1))
    except ValueError as value_error:
        flash(f"Value error: {str(value_error)}", "error")
        print(f"Value error: {value_error}")
        return redirect(url_for("index", page=1))
    except GrammarCheckError as grammar_error:
        flash(f"Grammar check error: {str(grammar_error)}", "error")
        print(f"Grammar check error: {grammar_error}")
        return redirect(url_for("index", page=1))

    new_file = FileUpload(
        file_name=unique_filename,
        user_id=current_user.id,
        file_path=file_path,
        file_size=formatted_size,
        corrections=corrections,
        upload_time=datetime.now(),
    )
    db.session.add(new_file)
    db.session.commit()
    session["file_id"] = new_file.id
    print(f"Created new file record: {unique_filename}, for user {current_user.id}")

    return redirect(url_for("index", page=1))


@file_blueprint.route("/download/<int:file_id>")
def download_file(file_id):
    file = FileUpload.query.get_or_404(file_id)
    return send_from_directory(
        current_app.config["UPLOAD_FOLDER"], file.file_name, as_attachment=True
    )


@file_blueprint.route("/delete/<int:file_id>")
def delete_file(file_id):
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
    return redirect(
        url_for("index", page=1)
    )  # return redirect(url_for("file_blueprint.index"))


@file_blueprint.route("/corrections/<int:file_id>")
def get_corrections(file_id):
    file = FileUpload.query.get_or_404(file_id)
    corrections = file.corrections
    page = 1
    per_page = 10
    files_query = FileUpload.query.filter_by(user_id=current_user.id)
    files_pagination = files_query.paginate(
        page=page, per_page=per_page, error_out=False
    )

    files = files_pagination.items
    total_pages = files_pagination.pages if files_pagination.pages is not None else 1

    sort = "upload_time"
    descending = "false"

    return render_template(
        "index.html",
        files=files,
        corrections=corrections,
        current_user=current_user,
        total_pages=total_pages,
        current_page=page,
        sort=sort,
        descending=descending,
    )


@file_blueprint.route("/")
def index():
    files = (
        FileUpload.query.filter_by(user_id=current_user.id)
        .order_by(FileUpload.upload_time.desc())
        .all()
    )
    file_id = session.get("file_id")
    corrections = None
    page = 1
    per_page = 10
    files_query = FileUpload.query.filter_by(user_id=current_user.id)
    files_pagination = files_query.paginate(
        page=page, per_page=per_page, error_out=False
    )

    files = files_pagination.items
    total_pages = files_pagination.pages if files_pagination.pages is not None else 1

    sort = "upload_time"
    descending = "false"
    if file_id:
        file = FileUpload.query.get(file_id)
        if file and file.user_id == current_user.id:
            corrections = file.corrections

    return render_template(
        "index.html",
        files=files,
        corrections=corrections,
        current_user=current_user,
        total_pages=total_pages,
        current_page=page,
        sort=sort,
        descending=descending,
    )


# Add this route for deleting selected files
@file_blueprint.route("/download-selected-files", methods=["POST"])
def download_selected_files():
    file_ids = request.form.get("file_ids_download", "").split(",")
    file_ids = [int(file_id) for file_id in file_ids if file_id.isdigit()]

    # Delete selected files from the database
    for file_id in file_ids:
        file_to_delete = FileUpload.query.get(file_id)
        if file_to_delete:
            # Temporary storage for zip file
            temp_dir = tempfile.mkdtemp()
            zip_filename = os.path.join(temp_dir, "selected_files.zip")

            with ZipFile(zip_filename, "w") as zipf:
                for file_id in file_ids:
                    file = FileUpload.query.get(file_id)
                    if file and os.path.exists(file.file_path):
                        zipf.write(file.file_path, arcname=file.file_name)
                        print(f"File added to zip: {file.file_path}")
                    else:
                        print(f"File not found or path is incorrect: {file.file_path}")
    flash(
        f"Selected files IDS: {file_ids} have been downloaded successfully", "success"
    )
    return send_file(
        zip_filename,
        as_attachment=True,
        mimetype="application/zip",
        download_name="selected_files.zip",
    )


def get_file_by_id(file_id):
    # Implement logic to retrieve file information by ID
    return FileUpload.query.get(file_id)


# Add this route for deleting selected files
@file_blueprint.route("/delete-selected-files", methods=["POST"])
def delete_selected_files():
    file_ids = request.form.get("file_ids_delete", "").split(",")
    file_ids = [int(file_id) for file_id in file_ids if file_id.isdigit()]

    # Delete selected files from the database
    for file_id in file_ids:
        file_to_delete = FileUpload.query.get(file_id)
        if file_to_delete:
            # Delete the file from storage or perform any additional cleanup
            # Note: This does not handle file deletion from the storage, adjust as needed
            # Example: file_to_delete.delete_from_storage()

            # Delete the file from the database
            db.session.delete(file_to_delete)

    db.session.commit()
    flash("Selected files have been deleted successfully", "success")
    flash(f"Deleted file IDs: {file_ids}", "success")
    return redirect(url_for("index"))
    # return send_file(zip_filename, as_attachment=True, mimetype='application/zip', download_name='selected_files.zip')
