import logging
from logging import handlers
from string import Template
import collections
import os

LOGGER_ROOT = "/var/log/openreality"
LOGGING_LEVEL = [
    logging.DEBUG,      # 10
    logging.INFO,       # 20
    logging.WARNING,    # 30
    logging.ERROR,      # 40
    logging.CRITICAL    # 50
]
LOGGER_TEMPLATE = Template('[$name]: $msg')

"""
    Logging Client is basically a wrapper around the IPCApp
"""
class LoggingClient():
    def __init__(self, name: str, when: str = "midnight"):
        # logger
        self._name = name
        self._when = when
        """
            Documentation:
            https://docs.python.org/3/library/logging.handlers.html#timedrotatingfilehandler
        """
        self._logger = logging.getLogger("server")
        self._logger.setLevel(logging.DEBUG)
        self._handler = handlers.TimedRotatingFileHandler(
            os.path.join(LOGGER_ROOT, self._name),
            backupCount=5, # max 5 days
            when=self._when,
            interval=1
        )
        self._handler.suffix = "%Y-%m-%d.log"
        self._formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        self._handler.setFormatter(self._formatter)
        self._logger.addHandler(self._handler)

    def log(self, level: int, msg: str) -> bool:
        # test for value error
        if level not in LOGGING_LEVEL:
            raise ValueError("Wrong logging level")
            return False
        self._logger.log(
            level=level,
            msg=LOGGER_TEMPLATE.substitute(name="test",msg=msg)
        )

