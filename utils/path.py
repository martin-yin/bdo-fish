import os

def root_path():
    current_path = os.path.dirname(os.path.abspath(__file__))
    root_path = os.path.dirname(current_path)
    return root_path
