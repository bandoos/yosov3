import os
from yoso.console import console
from fastapi import UploadFile, HTTPException
import logging
from typing import List


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


class EndpointLogFilter(logging.Filter):
    """A logging filter to exlcude a list of endpoints.
    """

    def __init__(self, endpoints: List[str]):
        self.excluded_endpoints = endpoints

    def filter(self, record):
        # remote_address = record.args[0]
        request_method = record.args[1]
        query_string = record.args[
            2]  # complete query string (so parameter and other value included)
        # html_version = record.args[3]
        # satuts_code = record.args[4]
        keep = not query_string in self.excluded_endpoints

        return keep
