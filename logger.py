import logging
import configparser
import datetime

log_file_path = "data/app.log"

def setup_logger(name, log_file=log_file_path, level=logging.DEBUG):
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

def is_week_since_last_clear(config_file='data/config.ini'):
    # Create a ConfigParser object
    config = configparser.ConfigParser()

    # Read the config file
    config.read(config_file)

    # Check if the 'last_cleared_date' exists
    if 'Logger' in config and 'last_cleared_date' in config['Logger']:
        last_cleared_date = datetime.datetime.fromisoformat(config['Logger']['last_cleared_date'])
    else:
        # If the date is not found, assume it's been more than a week
        return True

    # Get the current datetime
    current_datetime = datetime.datetime.now()

    # Calculate the difference in days
    days_difference = (current_datetime - last_cleared_date).days

    # Check if a week has passed (7 days or more)
    return days_difference >= 7

def store_last_cleared_date(config_file='data/config.ini'):
    # Get the current datetime
    current_datetime = datetime.datetime.now().isoformat()

    # Create a ConfigParser object
    config = configparser.ConfigParser()

    # Read the existing config file or create a new one
    config.read(config_file)
    
    if 'Logger' not in config:
        config['Logger'] = {}

    # Store the current datetime
    config['Logger']['last_cleared_date'] = current_datetime

    # Write the updated configuration back to the file
    with open(config_file, 'w') as f:
        config.write(f)

def clear_log_file(log_file):
    """
    Clears the content of the specified log file.

    Args:
        log_file (str): The path to the log file.
    """
    with open(log_file, 'w'):
        pass  # Truncate the file to zero length
