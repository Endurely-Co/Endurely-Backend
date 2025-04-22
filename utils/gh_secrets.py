import os


class GHSecrets:
    def __init__(self):
        pass

    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_USERNAME = os.getenv('DB_USERNAME')
    DB_NAME = os.getenv('DB_NAME')
    DB_HOST = os.getenv('DB_HOST')

    GEMINI_KEY = os.getenv('GEMINI_KEY')
