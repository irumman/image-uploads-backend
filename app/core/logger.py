import logging

from app.configs.settings import settings


class Logger:

    _instance: "Logger" = None

    def __new__(cls) -> "Logger":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            logging.basicConfig(
                level=settings.log_level.upper(),
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )

        return cls._instance

    def get_logger(self, name: str) -> logging.Logger:
        return logging.getLogger(name)


logger = Logger().get_logger(__name__)

__all__ = ["Logger", "logger"]
