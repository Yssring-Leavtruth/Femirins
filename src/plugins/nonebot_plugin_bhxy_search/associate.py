
from typing import Sequence
from unittest import result
from ..nonebot_plugin_utlie import config, Mongo


class RepeatException(Exception):

    def __init__(self, *args: Sequence) -> None:
        super().__init__(*args)
        self.repeated = args[0]


class Associate:

    @classmethod
    def append(cls, keywords: Sequence[str], equips: Sequence[Sequence[str]], user_id: str):
        with Mongo("keywords") as mongo:
            repeated = []

            for keyword in keywords:
                associated = [{"id": i[0], "rarity": i[1], "title": i[2],
                               "user_id": user_id} for i in equips]

                if result := mongo.db.find_one({"keyword": keyword}):
                    repeated += [i for i in associated if i["id"]
                                 in (a["id"] for a in result["associated"])]

                    mongo.db.update_one(
                        {"keyword": keyword},
                        {"$push": {"associated": {
                            "$each": [i for i in associated if i not in repeated]
                        }}}
                    )

                else:
                    mongo.db.insert_one(
                        {"keyword": keyword, "associated": associated})

            if repeated:
                raise RepeatException(repeated)

    @classmethod
    def delete(cls, keywords: Sequence[str], equips: Sequence[Sequence[str]], user_id: str):
        with Mongo("keywords") as mongo:
            for keyword in keywords:
                if result := mongo.db.find_one({"keyword": keyword}):
                    associated = [{"id": i[0], "rarity": i[1], "title": i[2],
                                   "user_id": user_id} for i in equips]

                    mongo.db.update_one(
                        {"keyword": keyword},
                        {"$pullAll": {"associated": associated}}
                    )

    @classmethod
    def find(cls, keyword: str):
        with Mongo("keywords") as mongo:
            if result := mongo.db.find_one({"keyword": keyword}):
                return [i["id"] for i in result["associated"]]
