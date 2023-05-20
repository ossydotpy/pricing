import logging

def logging_setup(log_file, log_name):
    # Create the logger and set its level
    logger = logging.getLogger(log_name)
    logger.setLevel(logging.INFO)

    # Create the file handler
    handler = logging.FileHandler(log_file)

    # Create the formatter and add it to the handler
    dt_fmt = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter("[{asctime}] [{levelname:<8}] {name}: {message}", dt_fmt, style="{")
    handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(handler)

    return logger