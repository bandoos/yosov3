"""
Module defining configuration parameters for the application.

configuration can be overriden via env variables with the prefix `YOSO_`
followed by the name of the of the configuration parameter field


"""
from pydantic import BaseSettings


class ServerConfig(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 8000
    dev_mode: bool = False
    upload_dir: str = "/tmp/yoso_image_upload"
    title: str = 'Deploying a ML Model with FastAPI'
    hanlder: str = "yoso.core:app"

    class Config:
        env_prefix = "YOSO_"
