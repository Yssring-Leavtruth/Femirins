
from re import L
import traceback
import httpx
from asyncio import create_task, gather
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from .setu_options import SetuOptions
from .setu_api import NoImageException, NoPainterException, RangeException, ConnectTimeoutException
from .lolicon import Lolicon
from .pixiv import Pixiv
from .pixiv_api import PixivApi
from ..nonebot_plugin_utlie import config


class SetuException(Exception):

    def __init__(self, tooltip: str, *args: object) -> None:
        super().__init__(*args)
        self.tooltip = tooltip


class Setu:

    def __init__(self, options: SetuOptions):
        self.setus = []
        self.options = options
        self.messages = []
        self.state = "unfinished"
        self.failed_message = ""
        self.image = ''
        self.painters = []
        self.Client = httpx.AsyncClient(proxies={"all://": config.proxy})

    async def get_setus(self):
        setus = []
        for API in [Lolicon, Pixiv]:

            if self.options.quantity_completed < self.options.amount:
                if self.options.search_pattern != "tag" and API == Lolicon:
                    continue

                try:
                    result = await API(self.options).main()
                    self.options.quantity_completed += len(result.setus)
                    setus += result.setus

                except NoImageException as e:
                    pass

        if not setus:

            raise SetuException(NoImageException(self.options.tags).tooltip)

        return setus

    async def get_image(self, client: httpx.AsyncClient, url: str):
        for i in range(3):
            try:
                response = await client.get(url)
                return MessageSegment.image(response.content)

            except httpx.TimeoutException:
                print("连接超时")
                print(traceback.format_exc())

            except httpx.ConnectError:
                print("连接错误")
                print(traceback.format_exc())

        raise ConnectTimeoutException()

    async def get_message(self, client: httpx.AsyncClient, setu: dict):
        image = await self.get_image(client, setu["url"])

        setu_info = Message.template(
            "标题：{title}\n画师：{painter}\npid：{pid}\n原图：{illust_url}"
        ).format_map({
            "title": setu["title"],
            "painter": setu["painter"],
            "pid": str(setu["pid"]),
            "illust_url": PixivApi.artworks + str(setu["pid"])
        })

        message = "排名: %s\n" % setu["rank"] + \
            setu_info if self.options.search_pattern == "ranking" else setu_info

        return image + "\n" + message

    async def get_messages(self):
        try:
            async with self.Client as client:
                tasks = [create_task(self.get_message(client, setu))
                 for setu in self.setus]
                return await gather(*tasks)

        except ConnectTimeoutException as e:
            raise SetuException(e.tooltip)

    async def __search_artworks_main(self):
        self.setus = await self.get_setus()
        yield self

        self.messages = await self.get_messages()
        yield self

    async def __search_painter_main(self):
        try:
            result = await Pixiv(self.options).main()
        except NoPainterException as e:
            raise SetuException(e.tooltip)
        except ConnectTimeoutException as e:
            raise SetuException(e.tooltip)

        yield self

        image = result.painters_image
        self.image = MessageSegment.image(image)
        self.painters = result.painters

        index = yield self

        await result.get_painter_works(self.painters[index]["id"])

        self.setus = result.setus
        self.options.quantity_completed += len(self.setus)

        yield self

        self.messages = await self.get_messages()

        yield self

    async def main(self):
        if self.options.search_pattern in ["tag", "ranking"]:
            return self.__search_artworks_main()
        else:
            return self.__search_painter_main()