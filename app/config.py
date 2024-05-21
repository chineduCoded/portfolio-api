import sys
from datetime import datetime
from functools import lru_cache
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from loguru import logger


class Settings(BaseSettings):
    database_name: str
    mongodb_uri: str
    github_oauth_url: str
    github_oauth_client_id: str
    github_oauth_client_secret: str
    redirect_uri: str
    client_origin: str
    jwt_secret_key: str
    jwt_refresh_secret_key: str
    token_url: str
    root_path: str = ""
    logging_level: str = "DEBUG"
    testing: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()

# class LogConfig(BaseModel):
#     """Logging configuration to be set for the server"""

#     LOGGER_NAME: str = "myportfolioapp"
#     LOG_FORMAT: str = "%(levelname)s | %(process)d | %(thread)d | %(asctime)s | %(message)s"
#     LOG_LEVEL: str = "DEBUG"

#     # Logging config
#     version: int = 1
#     disable_existing_loggers: bool = False
#     formatters: dict = {
#         "default": {
#             "()": "uvicorn.logging.DefaultFormatter",
#             "fmt": LOG_FORMAT,
#             "datefmt": "%Y-%m-%d %H:%M:%S",
#         },
#         "file_formatter": {
#             "()": "logging.Formatter",
#             "fmt": LOG_FORMAT,
#             "datefmt": "%Y-%m-%d %H:%M:%S",
#         },
#     }
#     handlers: dict = {
#         "default": {
#             "formatter": "default",
#             "class": "logging.StreamHandler",
#             "stream": "ext://sys.stderr",
#         },
#         "file": {
#         "formatter": "file_formatter",
#         "class": "logging.FileHandler",
#         "filename": "myportfolioapp.log",
#     },

#     }
#     loggers: dict = {
#         LOGGER_NAME: {"handlers": ["default", "file"], "level": LOG_LEVEL},
#     }


class LoguruLogConfig:
    """Logging configuration to be set for the server"""

    LOGGER_NAME: str = "myportfolioapp"
    LOG_FORMAT = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}.{function}:{line} | {message}"
    LOG_LEVEL: str = "DEBUG"
    LOG_RETENTION: str = "1 day"

    def configure(self):
        # Configure loguru with format and level
        logger.add(
            sink=sys.stderr,
            level=self.LOG_LEVEL,
            format=self.LOG_FORMAT,
        )
        logger.add(
            sink="myportfolioapp.log",
            level=self.LOG_LEVEL,
            format="{time:%d/%m/%Y at %H:%M:%S} | {level} | {module}.{function}:{line} | {message}",
            retention=self.LOG_RETENTION,
        )