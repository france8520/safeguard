import os

def get_complete_path(relative_path):
    """
    Convert relative path to absolute path based on the current file location
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, relative_path)

def read_wordList(filename):
    """
    Read words from a file and return as a list
    Each word should be on a new line
    """
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return [line.strip().lower() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"Warning: {filename} not found")
        return []

def ensure_dir_exists(directory):
    """
    Create directory if it doesn't exist
    """
    if not os.path.exists(directory):
        os.makedirs(directory)