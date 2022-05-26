from pymongo.mongo_client import MongoClient
from .config import config

class Mongo:

    def __init__(self, collection_name) -> None:
        self.client = MongoClient(config.database)
        self.db = self.client["Femirins"][collection_name]

    def __enter__(self):
        return self

    def __exit__(self, exc_tyep, exc_val, exc_tb):
        self.client.close()
