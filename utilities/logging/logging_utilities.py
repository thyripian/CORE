import functools
import logging
import os

# Define a custom logging level, ensuring it doesn't conflict with built-in levels
SESSION_LEVEL_NUM = 35  # Between WARNING (30) and ERROR (40)
SESSION_LEVEL_NAME = "SESSION"

# Add custom level name (this associates the level number with a name)
logging.addLevelName(SESSION_LEVEL_NUM, SESSION_LEVEL_NAME)


def session(self, message, *args, **kws):
    """
    Log a message with severity 'SESSION_LEVEL_NUM'.
    To integrate this into the logging.Logger class, we attach this function to it.
    This allows us to call it like any other logging method.
    """
    if self.isEnabledFor(SESSION_LEVEL_NUM):
        self._log(SESSION_LEVEL_NUM, message, args, **kws)


# Attach our custom logging method to the Logger class
logging.Logger.session = session


def setup_logging(log_directory, log_filename, level=logging.INFO):
    """
    Sets up the logging configuration for the application, ensuring all logs go to the specified file.
    """
    log_path = os.path.join(log_directory, log_filename)

    # Ensure the directory exists
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    # Clear existing handlers, if any
    logging.root.handlers = []

    # Set up file handler
    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(level)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)

    # Configure root logger
    logging.basicConfig(level=level, handlers=[file_handler])

    # UNCOMMENT FOR CONSOLE LOGGING
    # console_handler = logging.StreamHandler()
    # console_handler.setLevel(logging.DEBUG)  # Or another appropriate level
    # console_handler.setFormatter(formatter)
    # logging.getLogger().addHandler(console_handler)


def init_logging(logger):
    """
    Initialize specific logging entries at the start of the application.
    """
    logger.info("\n\nCENTRALIZED OPERATIONAL REPORTING ENGINE (CORE)\n\n")
    logger.session("\n\n\t\t\t“Do or do not, there is no try.”\n\n")
    logger.session("Developed by Kevan White - @thyripian")
    logger.session("Current as of: 07 October 2024")


def error_handler(func=None, *, default_return_value=None, reraise=False):
    if func is None:
        return functools.partial(
            error_handler, default_return_value=default_return_value, reraise=reraise
        )

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        try:
            return func(*args, **kwargs)
        except Exception as e:
            class_name = ""
            if args and hasattr(args[0], "__class__"):
                class_name = args[0].__class__.__name__
            func_name = f"{class_name}.{func.__name__}" if class_name else func.__name__
            logger.exception(f"An error occurred in {func_name}: {e}")
            if reraise:
                raise
            return default_return_value

    if isinstance(func, classmethod):
        return classmethod(wrapper)
    else:
        return wrapper
