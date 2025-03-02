import time
import logging
import random

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

    try:
        # Log some messages
        for i in range(20):
            log_func, message = random.choice(log_levels)
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
