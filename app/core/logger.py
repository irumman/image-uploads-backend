import logging

class Logger:
    _configured = False

    @classmethod
    def _configure(cls) -> None:
        if not cls._configured:
            logging.basicConfig(level=logging.INFO)
            cls._configured = True

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        cls._configure()
        return logging.getLogger(name)
