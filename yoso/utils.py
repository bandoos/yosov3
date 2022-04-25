import os
from yoso.console import console
from fastapi import UploadFile, HTTPException


def ensure_upload_dir(the_dir):
    """Ensure `the_dir` exists."""
    if not os.path.exists(the_dir):
        console.log(f"[green]Creating dir {the_dir}[/]")
        os.mkdir(the_dir)


def validate_image_file(file: UploadFile, exts={"jpg", "jpeg", "png"}):
    """Validate the extension of the some uploaded file."""
    filename = file.filename
    fileExtension = filename.split(".")[-1] in exts
    if not fileExtension:
        raise HTTPException(status_code=415,
                            detail="Unsupported file provided.")
