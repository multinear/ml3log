# ML3Log

A minimal Python logging package that provides both console logging and a web interface to view logs.

## Features

- Standard Python logger compatible
- Web server for viewing logs in real-time
- Minimal footprint with no external dependencies
- Configurable port (default: 6020)
- Monkey patching support for standard logging module

## Installation

```bash
pip install ml3log
```

## Usage

### Starting the server

```python
import ml3log

# Start the server on the default port (6020)
ml3log.start_server()

# Or specify a custom port
ml3log.start_server(port=8080)
```

### Using the logger

```python
import ml3log
import logging

# Get a logger with default settings
logger = ml3log.get_logger("my_app")

# Or customize the logger
logger = ml3log.get_logger(
    name="my_app",
    level=logging.DEBUG,
    host="localhost",
    port=6020
)

# Alternatively, monkey patch the standard logging module
# to capture logs from libraries using standard logging
ml3log.monkey_patch_logging()

# Use like a standard Python logger
logger.info("This is an info message")
logger.warning("This is a warning")
logger.error("This is an error")
logger.debug("This is a debug message")

# Log exceptions
try:
    1/0
except Exception as e:
    logger.exception("An error occurred")
```

### Viewing logs

Open your browser and navigate to:

```
http://localhost:6020
```

The web interface will automatically update with new logs as they arrive.

## License

MIT
