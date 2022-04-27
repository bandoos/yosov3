from pydantic import BaseSettings
from typing import Set


class ClientConfig(BaseSettings):
    """Configuration class for the yoso client
    """
    host: str = "0.0.0.0"
    port: int = 8000
    model: str = "yolov3-tiny"
    response_image_dir: str = "./images_predicted"
    accepted_formats: Set[str] = {".jpg", ".jpeg", ".png"}

    class Config:
        env_prefix = "YOSO_CLIENT_"
