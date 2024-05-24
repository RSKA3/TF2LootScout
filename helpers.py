import os

def check_if_file_exists(file_path: str) -> bool:
    """
    Checks if path exists
    
    Args:
        log_file (str): absolute log file path
    
    Returns:
        True if exists, False if not
    """

    if os.path.exists(file_path):
        print(f"file: {file_path} exists")
        return True
    
    print(f"file: {file_path} does not exists")
    return False

def create_file(file_path: str) -> bool:
    """
    Tries to create file
    
    Args:
        log_file (str): absolute log file path
    
    Returns:
        True if success, False if not
    """

    try:
        # Open the file in write mode, which will create the file if it does not exist
        with open(file_path, 'w') as file:
            file.write("")
        print(f"The file '{file_path}' has been created.")
        return True
    except OSError as e:
        print(f"An error occurred: {e}")
        return False

