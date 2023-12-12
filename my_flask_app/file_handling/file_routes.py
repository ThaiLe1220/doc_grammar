""" Filename: file_routes.py - Directory: my_flask_app/file_handling

This module defines routes for file upload, download, deletion, and correction retrieval.
"""
import os
from flask import (
    Blueprint,
    jsonify,
    render_template,
    send_from_directory,
    redirect,
    url_for,
    flash,
    request,
    current_app,
)
from werkzeug.utils import secure_filename
from database.models import db, FileUpload
from utils.docx_utils import correct_text_grammar
from utils.exceptions import GrammarCheckError

file_blueprint = Blueprint("file_blueprint", __name__)


@file_blueprint.route("/upload", methods=["POST"])
def upload_file():
    """Upload a file and check its content for grammar corrections.

    Returns:
        redirect: Redirects to the index page after processing the file.
    """
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
        existing_file.corrections = corrections
    else:
        new_file = FileUpload(
            file_name=filename, file_path=file_path, corrections=corrections
        )
        db.session.add(new_file)

    db.session.commit()
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
    return jsonify(corrections)


@file_blueprint.route("/")
def index():
    """Display a list of files.

    Returns:
        render_template: HTML page displaying a list of files.
    """
    files = FileUpload.query.all()
    return render_template("index.html", files=files)
