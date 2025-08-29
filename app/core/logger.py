import logging


class Logger:
    """Singleton logger provider."""

    _instance: "Logger" | None = None

    def __new__(cls) -> "Logger":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            logging.basicConfig(level=logging.INFO)
        return cls._instance

    def get_logger(self, name: str) -> logging.Logger:
        return logging.getLogger(name)


logger = Logger().get_logger(__name__)

__all__ = ["Logger", "logger"]
