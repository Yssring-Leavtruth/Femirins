
import httpx
from typing import Union, List, Dict, Any
from nonebot.log import logger as nonebot_logger
from .setu_api import SetuAPI
from .setu_options import SetuOptions


class Lolicon(SetuAPI):

    def __init__(self, options: SetuOptions) -> None:
        super().__init__(options)

        self.lolicon_url = "https://api.lolicon.app/setu/v2"

    async def get_setu(self):
        params = {
            "num": 100,
            "tag": self.options.tags,
            "size": self.config.setu_size,
            "r18": 0
        }

        nonebot_logger.info("（lolicon）正在获取涩图...")
        response = httpx.get(self.lolicon_url, params=params)

        pooling = response.json()["data"]
        nonebot_logger.info("（lolicon）查询到%s张涩图" % len(pooling))  
        return pooling

    def filter(self, pooling: List[Dict[str, Any]]):
        return super().filter(pooling, lambda i: str(i["pid"]) not in self.records)

    def format(self, pooling: List[Dict[str, Any]]):
        return super().format(pooling, lambda i: {
            'pid': i['pid'],
            'title': i['title'],
            'painter': i['author'],
            'url': i['urls'][self.config.setu_size]
        })

    async def main(self):
        pooling = await self.get_setu()
        filtered = self.filter(pooling)
        self.setus = self.format(filtered)

        return self
