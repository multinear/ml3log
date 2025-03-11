# ML3Log

A minimal Python logging package that provides both console logging and a web interface to view logs.

## Features

- Standard Python logger compatible
- Web server for viewing logs in real-time
- Minimal footprint with no external dependencies
- Configurable port (default: 6020)
- Monkey patching support for standard logging module
- Command-line interface for quick server startup

## Installation

```bash
pip install ml3log
```

## Usage

### Starting the server

#### From Python code

```python
import ml3log

# Start the server on the default port (6020)
ml3log.start_server()

# Or specify a custom port
ml3log.start_server(port=8080)
```

#### From the command line

ML3Log can be started directly from the command line:

```bash
# Using the ml3log command (after installation)
ml3log

# Or with custom host and port
ml3log --host 0.0.0.0 --port 8080

# Alternatively, using the Python module syntax
python -m ml3log
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

### Sending logs from JavaScript

You can send logs directly from JavaScript to ML3Log using a simple fetch request:

```javascript
// Minimal example to send a log event to ML3Log
async function sendLog(message, level = 'INFO', loggerName = 'js-client') {
  const logEntry = {
    levelname: level,
    name: loggerName,
    message: message,
    created: Date.now() / 1000  // Current time in seconds
  };

  try {
    const response = await fetch('http://localhost:6020/traces', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(logEntry)
    });
    return response.ok;
  } catch (error) {
    console.error('Failed to send log:', error);
    return false;
  }
}

// Usage examples
sendLog('User clicked submit button');
sendLog('API request failed', 'ERROR');
sendLog('Debug information', 'DEBUG', 'frontend-app');
```

### Viewing logs

Open your browser and navigate to:

```
http://localhost:6020
```

The web interface will automatically update with new logs as they arrive.

<img src="static/screenshot.png" alt="Screenshot" width="800" />

## License

[MIT](LICENSE)
