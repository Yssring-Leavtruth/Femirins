import time
from nonebot import get_driver
from ..nonebot_plugin_utlie import config, Mongo

class Record:

    @classmethod
    def get_records(cls):

        with Mongo("setu_records") as mongo:
            res = mongo.db.find_one()
            now_day = int(time.strftime('%Y%m%d', time.localtime()))

            if res is None:
                mongo.db.insert_one({'day': now_day, 'pool': []})
            elif now_day - res['day'] >= 3:
                mongo.db.update_one({}, {'$set': {'day': now_day, 'pool': []}})
            else:
                return res['pool']

            return []

    @classmethod
    def save(cls, data):

        with Mongo("setu_records") as mongo:
            for i in data:
                mongo.db.update_one({}, {'$addToSet': {'pool': i}})