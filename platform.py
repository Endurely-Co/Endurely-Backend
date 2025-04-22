import os


def is_github():
    return os.getenv("GITHUB_ACTIONS") == "true"
