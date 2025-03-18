import logging
import time
import json
import traceback
from datetime import datetime

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
    log_levels = [
        (logger.debug, "Debug message"),
        (logger.info, "Info message"),
        (logger.warning, "Warning message"),
        (logger.error, "Error message"),
        (logger.critical, "Critical message"),
    ]

    # Demonstrate all log levels
    logger.info("=== Demonstrating all log levels ===")
    for i, (log_func, message) in enumerate(log_levels):
        log_func(f"{message} #{i+1}")
        time.sleep(0.5)

    # Demonstrate all highlighting features
    logger.info("=== Demonstrating all highlighting features with standard logging ===")

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
    logger.info("JSON example: %s", json.dumps(sample_json, indent=2))

    # ISO timestamp highlighting
    current_time = datetime.now().isoformat()
    logger.info("ISO timestamp example: %s", current_time)

    # File path highlighting (with and without line numbers)
    logger.info(
        "File path example: /Users/johndoe/ml3log/example2.py"
    )
    logger.info(
        "File path with line number: /Users/johndoe/ml3log/example2.py:42"
    )

    # File path with quotes
    logger.info(
        "File path with quotes: '/Users/johndoe/ml3log/example2.py'"
    )
    logger.info(
        'File path with double quotes: "/Users/johndoe/ml3log/example2.py:25"'
    )

    # URL highlighting (clickable)
    logger.info("URL example: https://github.com/multinear/ml3log")
    logger.info("Documentation URL: https://docs.python.org/3/library/logging.html")

    # Combined example
    logger.info(
        "Combined example: timestamp %s, "
        "file /Users/johndoe/ml3log/example2.py:50, "
        "and URL https://multinear.com",
        current_time,
    )

    # Try with another logger
    another_logger = logging.getLogger("another_module")
    another_logger.info("Logs from another module")

    # Demonstrate exception logging
    try:
        1 / 0
    except Exception as e:
        logger.exception("Caught an exception: %s", str(e))

    # Compare with direct ml3log usage
    ml3_logger = ml3log.get_logger("direct_ml3log")
    ml3_logger.info("This log is sent directly via ml3log")

    # Also demonstrate highlighting with direct ml3log usage
    ml3_logger.info(
        "=== Demonstrating all highlighting features with direct ml3log ==="
    )
    ml3_logger.info("JSON example: %s", json.dumps(sample_json, indent=2))
    ml3_logger.info(
        "URL and file path: https://multinear.com and "
        "/Users/johndoe/ml3log/logger.py:128"
    )
    
    # Demonstrate truncation for long log messages
    logger.info("=== Demonstrating log truncation for long messages ===")
    
    # Example 1: Long multi-line log message
    long_text = "\n".join([f"This is line {i} of a very long log message" for i in range(1, 20)])
    logger.info("Long multi-line message:\n%s", long_text)
    
    # Example 2: Very long single line
    long_single_line = "This is a very long single line log message that exceeds the character limit. " * 10
    logger.info("Long single line: %s", long_single_line)
    
    # Example 3: Long error traceback
    try:
        # Intentionally cause a deep error traceback
        def level1(): return level2()
        def level2(): return level3()
        def level3(): return level4()
        def level4(): return level5()
        def level5(): return level6()
        def level6(): return level7()
        def level7(): return level8()
        def level8(): return level9()
        def level9(): return level10()
        def level10(): return 1/0
        
        level1()
    except Exception as e:
        error_traceback = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        logger.error("Complex error with long traceback:\n%s", error_traceback)
    
    # Example 4: Long JSON output
    large_json = {
        "data": [
            {
                "id": i,
                "name": f"Item {i}",
                "attributes": {
                    "created": datetime.now().isoformat(),
                    "values": [j for j in range(20)],
                    "metadata": {
                        "description": "This is a very long description " * 5,
                        "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"]
                    }
                }
            } for i in range(10)
        ]
    }
    logger.info("Large JSON payload:\n%s", json.dumps(large_json, indent=2))

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
