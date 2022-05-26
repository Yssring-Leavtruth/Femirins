
from asyncio import gather
from motor.motor_asyncio import AsyncIOMotorClient
from .associate import Associate
from .search_options import SearchOptions
from ..nonebot_plugin_utlie import config


class SearchEquips:

    @classmethod
    async def search(cls, options: SearchOptions):
        client = AsyncIOMotorClient(config.database)
        database = client["Femirins"]["equips"]
        key_names = ["title", 'prop1.maxLvDesc',
                     'prop2.maxLvDesc', 'prop6.maxLvDesc', 'prop7.maxLvDesc']

        if options.keywords and not isinstance(options.keywords, str):
            cursors = [database.find(options.toDict(key)) for key in key_names]

            if ids := Associate.find(options.keywords.pattern):
                print(options.toDict(ids=ids))
                cursors.append(database.find(options.toDict(ids=ids)))

        else:
            cursors = [database.find(options.toDict())]

        tasks = [cursor.to_list(4000) for cursor in cursors]
        result = sum(await gather(*tasks), [])

        client.close()

        if result:
            result = [i for i in result if i["type"] != "servant"]
            result = [v for i, v in enumerate(result) if v not in result[:i]]
            result.sort(key=lambda i: int(i["id"]), reverse=True)

            order = {"arms": 1, "clothes": 2, "badge": 3}
            result.sort(key=lambda i: order[i["type"]])

            print([i["title"] for i in result])
            data = []
            for i in range(len(result)):

                if i > 0 and result[i]["title"] == result[i - 1]["title"]:
                    continue
                if i + 1 < len(result) and result[i]["title"] == result[i + 1]["title"]:
                    data.append((result[i], result[i + 1]))
                else:
                    data.append((result[i],))

            return data[:40] if len(data) > 40 else data

        else:
            return []
