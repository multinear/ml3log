import logging
import time

# Import ml3log and start the server
import ml3log


def main():
    # Start the server
    ml3log.start_server(port=6020)

    # Monkey patch the standard logging module
    ml3log.monkey_patch_logging(level=logging.DEBUG)

    # Use the standard logging module
    logging.info("This log is NOT sent to ML3Log")

    # Create a logger using the standard logging module
    logger = logging.getLogger("example_standard")
    logger.info("This also works with named loggers")

    # Log at different levels
    logger.debug("Debug message")
    logger.warning("Warning message")
    logger.error("Error message")

    # Try with another logger
    another_logger = logging.getLogger("another_module")
    another_logger.info("Logs from another module")

    # Demonstrate exception logging
    try:
        1 / 0
    except Exception as e:
        logger.exception(f"Caught an exception: {str(e)}")

    # Compare with direct ml3log usage
    ml3_logger = ml3log.get_logger("direct_ml3log")
    ml3_logger.info("This log is sent directly via ml3log")

    print("\nOpen your browser at http://localhost:6020 to view logs")
    print("Press Ctrl+C to exit.")

    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nRestoring original logging")
        ml3log.restore_logging()
        print("Exiting...")


if __name__ == "__main__":
    main()
