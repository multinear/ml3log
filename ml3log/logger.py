import logging
import json
import socket
import threading
import functools
from http.client import HTTPConnection
from typing import Optional, Dict


class ML3LogHandler(logging.Handler):
    """
    A logging handler that sends logs to the ML3Log server.
    """

    def __init__(self, host: str = 'localhost', port: int = 6020):
        super().__init__()
        self.host = host
        self.port = port
        self.connection = None
        self._connection_lock = threading.Lock()

    def _get_connection(self) -> HTTPConnection:
        """Get or create an HTTP connection to the ML3Log server."""
        with self._connection_lock:
            if self.connection is None:
                self.connection = HTTPConnection(self.host, self.port)
            return self.connection

    def emit(self, record: logging.LogRecord) -> None:
        """Send the log record to the ML3Log server."""
        try:
            # Format the record as a dictionary
            log_entry = {
                'created': record.created,
                'name': record.name,
                'levelname': record.levelname,
                'levelno': record.levelno,
                'message': self.format(record),
                'pathname': record.pathname,
                'lineno': record.lineno,
                'funcName': record.funcName,
                'process': record.process,
                'processName': record.processName,
                'thread': record.thread,
                'threadName': record.threadName,
                'hostname': socket.gethostname(),
            }

            # Add exception info if available
            if record.exc_info:
                log_entry['exc_info'] = self.formatter.formatException(record.exc_info)

            # Convert to JSON
            json_data = json.dumps(log_entry).encode('utf-8')

            # Send to the server
            try:
                conn = self._get_connection()
                conn.request(
                    'POST',
                    '/traces',
                    json_data,
                    {
                        'Content-Type': 'application/json',
                        'Content-Length': str(len(json_data)),
                    },
                )
                response = conn.getresponse()
                response.read()  # Read and discard the response
            except Exception:
                # If connection fails, reset it so we can try again next time
                with self._connection_lock:
                    if self.connection:
                        self.connection.close()
                        self.connection = None
                raise

        except Exception:
            self.handleError(record)


def get_logger(
    name: Optional[str] = None,
    level: int = logging.INFO,
    host: str = 'localhost',
    port: int = 6020,
) -> logging.Logger:
    """
    Get a logger that both prints logs and sends them to the ML3Log server.

    Args:
        name: The name of the logger (default: None, which uses the root logger)
        level: The logging level (default: INFO)
        host: The ML3Log server host (default: localhost)
        port: The ML3Log server port (default: 6020)

    Returns:
        A configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Clear existing handlers to avoid duplicates
    logger.handlers = []

    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # Add ML3Log handler
    ml3log_handler = ML3LogHandler(host, port)
    ml3log_handler.setLevel(level)
    ml3log_formatter = logging.Formatter('%(message)s')
    ml3log_handler.setFormatter(ml3log_formatter)
    logger.addHandler(ml3log_handler)

    return logger


# Store original getLogger function
_original_get_logger = logging.getLogger


def monkey_patch_logging(
    level: int = logging.INFO,
    host: str = 'localhost',
    port: int = 6020,
    console_output: bool = True,
) -> None:
    """
    Monkey patch the standard logging module to use ML3Log for all loggers.

    This function replaces the standard logging.getLogger function with a custom
    implementation that adds ML3Log handlers to all loggers created through it.

    Args:
        level: The default logging level (default: INFO)
        host: The ML3Log server host (default: localhost)
        port: The ML3Log server port (default: 6020)
        console_output: Whether to also output logs to console (default: True)
    """
    # Cache for loggers that have already been patched
    patched_loggers: Dict[str, bool] = {}

    @functools.wraps(_original_get_logger)
    def patched_get_logger(name: Optional[str] = None) -> logging.Logger:
        # Get the logger using the original function
        logger = _original_get_logger(name)

        # Skip if this logger has already been patched
        logger_key = name if name is not None else ''
        if logger_key in patched_loggers:
            return logger

        # Mark as patched
        patched_loggers[logger_key] = True

        # Set level if not already set
        if logger.level == logging.NOTSET:
            logger.setLevel(level)

        # Prevent propagation to avoid duplicate logs
        logger.propagate = False

        # Add console handler if requested
        if console_output and not any(
            isinstance(h, logging.StreamHandler) for h in logger.handlers
        ):
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logger.level)
            console_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)

        # Add ML3Log handler if not already present
        if not any(isinstance(h, ML3LogHandler) for h in logger.handlers):
            ml3log_handler = ML3LogHandler(host, port)
            ml3log_handler.setLevel(logger.level)
            ml3log_formatter = logging.Formatter('%(message)s')
            ml3log_handler.setFormatter(ml3log_formatter)
            logger.addHandler(ml3log_handler)

        return logger

    # Replace the standard getLogger function with our patched version
    logging.getLogger = patched_get_logger

    # Also patch the root logger
    root_logger = _original_get_logger()
    if not any(isinstance(h, ML3LogHandler) for h in root_logger.handlers):
        ml3log_handler = ML3LogHandler(host, port)
        ml3log_handler.setLevel(level)
        ml3log_formatter = logging.Formatter('%(message)s')
        ml3log_handler.setFormatter(ml3log_formatter)
        root_logger.addHandler(ml3log_handler)

    print(
        f"Standard logging module has been patched to use ML3Log (host: {host}, port: {port})"
    )


def restore_logging() -> None:
    """
    Restore the original logging.getLogger function.

    This function undoes the changes made by monkey_patch_logging.
    """
    logging.getLogger = _original_get_logger
    print("Standard logging module has been restored to its original state")
