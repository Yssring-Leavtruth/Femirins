
import re
import math
import traceback
import httpx
import random
from asyncio import create_task, gather
from typing import List, Dict, Any
from .setu_api import NoPainterException, SetuAPI, NoImageException, ConnectTimeoutException
from .setu_options import SetuOptions
from .pixiv_api import PixivApi
from .pixiv_config import PixivConfig
from .draw_painters import draw
from ..nonebot_plugin_utlie import config, pattern


class Pixiv(SetuAPI):

    def __init__(self, options: SetuOptions) -> None:
        super().__init__(options)

        self.painters = []
        self.painters_image = ''
        self.Client = httpx.AsyncClient(
            proxies={"all://": config.proxy},
            headers=PixivConfig.headers
        )

    async def get(self, client: httpx.AsyncClient, url: str, params={}):
        for i in range(3):
            try:
                response = await client.get(url, params=params)
                return response
            except httpx.TimeoutException:
                print("连接超时")
                print(traceback.format_exc())
            except httpx.ConnectError:
                print("连接错误")
                print(traceback.format_exc())

        raise ConnectTimeoutException()

    def filter(self, pooling: List[Dict[str, Any]]):
        return super().filter(pooling, lambda i: str(i["id"]) not in self.records)

    def format(self, pooling: List[Dict[str, Any]]):
        return super().format(pooling, lambda i: {
            'pid': i['id'],
            'title': i['title'],
            'painter': i['userName'],
            'url': PixivConfig.get_image_url(i["url"])
        })

    async def get_search_artworks_data(self):
        tags = " ".join(tag for tag in self.options.tags)
        params = {"p": 1}

        async with self.Client as client:
            response = await self.get(client, PixivApi.search_artworks + tags, params=params)
            illust = response.json()["body"]["illustManga"]
            total = illust["total"]
            page = math.ceil(total / 60)

            if page > 1:
                pooling = illust["data"]

                tasks = []
                for p in random.sample(range(2, page + 1), 5 if page > 5 else page - 1):
                    tasks.append(
                        create_task(self.get(
                            client,
                            PixivApi.search_artworks + tags, params={"p": p}
                        ))
                    )

                response_list = await gather(*tasks)

                return sum(
                    [r.json()["body"]["illustManga"]["data"]
                        for r in response_list],
                    pooling
                )

        raise NoImageException(self.options.tags)

    async def __search_artworks_main(self):
        pooling = await self.get_search_artworks_data()
        filtered = self.filter(pooling)
        self.setus = self.format(filtered)

        return self

    async def get_ranking_artworks_data(self):
        params = {
            "mode": self.options.ranking_pattern,
            "content": "illust",
            "p": 1,
            "format": "json"
        }

        async with self.Client as client:
            response = await self.get(client, PixivApi.ranking, params=params)
            total = response.json()["rank_total"]
            page = math.ceil(total / 50) if math.ceil(total / 50) < 5 else 5

            pooling = response.json()["contents"]

            if page > 1:
                tasks = []
                for i in range(2, page + 1):
                    p = {k: v for k, v in params.items()}
                    p["p"] = i

                    tasks.append(
                        create_task(self.get(
                            client,
                            PixivApi.ranking,
                            params=p
                        ))
                    )

                response_list = await gather(*tasks)

                return sum(
                    [r.json()["contents"] for r in response_list],
                    pooling
                )

        raise NoImageException(self.options.tags)

    async def __ranking_artworks_main(self):
        pooling = await self.get_ranking_artworks_data()
        filtered = super().filter(
            pooling, lambda i: i["illust_id"] not in self.records)
        self.setus = super().format(filtered, lambda i: {
            "rank": i["rank"],
            "pid": i["illust_id"],
            "title": i["title"],
            "painter": i["user_name"],
            "url": PixivConfig.get_image_url(i["url"])
        })

        return self

    async def get_painter_data(self, r: re.Match):
        url = re.sub(r'piximg.net', 'pixiv.cat', r.group("avatar"))
        response = await self.get(self.Client, url)

        return {
            "id": r.group("id"),
            "painter": r.group("painter"),
            "avatar": None if response is None else response.content,
            "works": r.group("works")
        }

    async def get_painters_data(self):
        params = {
            "s_mode": "s_usr",
            "nick": self.options.painter
        }

        response = await self.get(self.Client, PixivApi.search_user, params=params)
        if tasks := [create_task(self.get_painter_data(r))
                        for r in pattern.finditer(response.text)]:

            painters = await gather(*tasks)
            return [painters[i] for i in range(10)] if len(painters) > 10 else list(painters)

        else:
            raise NoPainterException(self.options.painter)

    async def get_painter_works(self, uid):
        response = await self.get(self.Client, PixivApi.user_all_artworks_id % uid)
        illust_ids = [k for k in response.json()["body"]["illusts"].keys()]

        if self.options.matcher_rule == "count":
            illust_ids = illust_ids if len(
                illust_ids) < 50 else illust_ids[:50]

        filtered = super().filter(illust_ids, lambda i: i not in self.records)

        params = {
            'work_category': 'illustManga',
            'is_first_page': 1,
            'lang': 'zh',
            'ids[]': filtered
        }

        res = await self.get(self.Client, PixivApi.user_artworks % uid, params=params)
        for v in res.json()["body"]["works"].values():
            self.setus.append({
                "pid": v["id"],
                "title": v["title"],
                "painter": v["userName"],
                "url": PixivConfig.get_image_url(v["url"])
            })

    async def __search_painter_main(self):
        self.painters = await self.get_painters_data()
        self.painters_image = draw(self.painters)

        return self

    async def main(self):
        if self.options.search_pattern == "tag":
            return await self.__search_artworks_main()

        elif self.options.search_pattern == "ranking":
            return await self.__ranking_artworks_main()

        elif self.options.search_pattern == "painter":
            return await self.__search_painter_main()

        else:
            return self
