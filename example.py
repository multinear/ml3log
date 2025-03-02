import time
import logging
import json
from datetime import datetime

import ml3log


def main():
    # Start the server
    ml3log.start_server(port=6020)

    # Get a logger
    logger = ml3log.get_logger("example_app", level=logging.DEBUG)

    logger.info("ML3Log example started")
    logger.info("Open your browser at http://localhost:6020 to view logs")

    # Generate some sample logs
    log_levels = [
        (logger.debug, "This is a debug message"),
        (logger.info, "This is an info message"),
        (logger.warning, "This is a warning message"),
        (logger.error, "This is an error message"),
        (logger.critical, "This is a critical message"),
    ]

    # Demonstrate all highlighting features
    logger.info("=== Demonstrating all highlighting features ===")

    # JSON properties highlighting
    sample_json = {
        "user": "example_user",
        "id": 12345,
        "is_active": True,
        "tags": ["important", "demo", "test"],
        "metadata": {
            "created_at": datetime.now().isoformat(),
            "version": "1.0.0",
            "settings": None,
        },
    }
    logger.info(f"JSON example: {json.dumps(sample_json, indent=2)}")

    # ISO timestamp highlighting
    current_time = datetime.now().isoformat()
    logger.info(f"ISO timestamp example: {current_time}")

    # File path highlighting (with and without line numbers)
    logger.info(
        "File path example: /Users/johndoe/ml3log/example.py"
    )
    logger.info(
        "File path with line number: /Users/johndoe/ml3log/example.py:42"
    )

    # File path with quotes
    logger.info(
        "File path with quotes: '/Users/johndoe/ml3log/example.py'"
    )
    logger.info(
        'File path with double quotes: "/Users/johndoe/ml3log/example.py:25"'
    )

    # URL highlighting (clickable)
    logger.info("URL example: https://github.com/multinear/ml3log")
    logger.info("Documentation URL: https://docs.python.org/3/library/logging.html")

    # Combined example
    logger.info(
        f"Combined example: timestamp {current_time}, "
        f"file /Users/johndoe/ml3log/example.py:50, "
        f"and URL https://multinear.com"
    )

    try:
        # Log some messages
        for i, (log_func, message) in enumerate(log_levels):
            log_func(f"{message} #{i+1}")
            time.sleep(1)

        # Demonstrate exception logging
        logger.info("Now demonstrating exception logging...")
        raise ValueError("This is a demonstration exception")
    except Exception as e:
        logger.exception(f"Caught an exception: {str(e)}")

    logger.info("Example complete. The server will continue running.")
    logger.info("Press Ctrl+C to exit.")

    # Keep the main thread alive
    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
