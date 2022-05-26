
from pydantic import BaseModel, Extra
from typing import List, Dict
from nonebot import get_driver

class Config(BaseModel, extra=Extra.ignore):
    superusers: List[str]
    nickname: List[str]
    setu_size: str
    setu_maximum: int
    setu_cooling_time: int
    setu_maximum_limit: int
    database: str
    proxy: str

config = Config.parse_obj(get_driver().config)
