
import time
from tomlkit import boolean
from ..nonebot_plugin_utlie import config, Mongo


class SessionDatabase:

    def __init__(self, user_id: str) -> None:
        self.id = user_id

    def get_session(self):
        with Mongo("setu_sessions") as mongo:
            if session := mongo.db.find_one({"user_id": self.id}):
                return session
            else:
                now = int(time.strftime('%Y%m%d', time.localtime()))
                session = {
                    "user_id": self.id,
                    "day": now,
                    "ts": -1,
                    "amount": 0,
                    "limit": config.setu_maximum_limit
                }
                mongo.db.insert_one(session)
                return session

    def update(self, data):
        with Mongo("setu_sessions") as mongo:
            mongo.db.update_one({"user_id": self.id}, {"$set": data})


class Session:

    def __init__(self, user_id: str) -> None:

        self.id = user_id
        self.database = SessionDatabase(self.id)
        self.session = self.database.get_session()
        self.day = self.session["day"]
        self.ts = self.session["ts"]
        self.limit = self.session["limit"]
        self.amount = self.session["amount"]

    def is_cooling(self) -> bool:

        if self.ts == -1:
            return False
        else:
            cooling_time = config.setu_cooling_time
            now = int(time.time())

            return False if now - self.ts > cooling_time * self.amount else True

    def is_limited(self) -> bool:

        now = int(time.strftime('%Y%m%d', time.localtime()))
        if now - self.day > 0:
            self.day = now
            self.limit = config.setu_maximum_limit

        return True if self.limit <= 0 else False

    def subtract(self, amount: int):

        self.limit -= amount
        self.amount = amount

    def save(self):

        session = {
            "day": self.day,
            "ts": int(time.time()),
            "limit": self.limit,
            "amount": self.amount
        }

        self.database.update(session)
