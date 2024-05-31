import logging
from logging import handlers
from string import Template
import collections
import threading
import os

LOGGER_ROOT = "/var/log/openreality"
LOGGER_TEMPLATE = Template('[$name]: $message')

class LoggingLevel():
    INFO = 0
    DEBUG = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4


"""
    Logging Client is basically a wrapper around the IPCApp
"""
#class LoggingClient():
class LoggingClient(threading.Thread):
    def __init__(self, name: str, when: str = "midnight", buffer=1000):
        # thread
        super().__init__()
        self._stop_cmd = threading.Event()

        # logger
        self._name = name
        self._when = when
        """
            Documentation:
            https://docs.python.org/3/library/logging.handlers.html#timedrotatingfilehandler
        """
        self._logger = logging.getLogger("server")
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

        # buffer
        self._buffer = collections.deque(maxlen=buffer)

    @property
    def is_busy(self):
        return len(self._buffer) > 0

    def log(self, level: int, message: str) -> bool:
        if level < LoggingLevel.INFO or level > LoggingLevel.CRITICAL:
            raise ValueError(f"Wrong logging level")
            return False
        self._buffer.append({level: message})
        return True

    def run(self):
        msg: Dict[int, str]= {}
        level: int = 0
        while not self._stop_cmd.is_set():
            # if buffer available start logging
            if len(self._buffer) > 0:
                msg = self._buffer.popleft()
                level = 
                
                # log
                if LoggingLevel.INFO in msg:
                    self._logger.info(
                        LOGGER_TEMPLATE.substitute(
                            name=self._name,
                            message=msg[LoggingLevel.INFO]
                        )
                    )
                elif LoggingLevel.DEBUG in msg:
                    self._logger.debug(
                        LOGGER_TEMPLATE.substitute(
                            name=self._name,
                            message=msg[LoggingLevel.DEBUG]
                        )
                    )
                elif LoggingLevel.WARNING in msg:
                    self._logger.warning(
                        LOGGER_TEMPLATE.substitute(
                            name=self._name,
                            message=msg[LoggingLevel.WARNING]
                        )
                    )
                elif LoggingLevel.ERROR in msg:
                    self._logger.error(
                        LOGGER_TEMPLATE.substitute(
                            name=self._name,
                            message=msg[LoggingLevel.ERROR]
                        )
                    )
                elif LoggingLevel.CRITICAL in msg:
                    self._logger.critical(
                        LOGGER_TEMPLATE.substitute(
                            name=self._name,
                            message=msg[LoggingLevel.CRITICAL]
                        )
                    )
        # end of the thread
        self._stop_cmd.clear()

    def stop(self):
        self._stop_cmd.set()
