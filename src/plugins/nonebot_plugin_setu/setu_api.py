
from random import sample
from typing import Callable, Union, List, Dict, Any
from .setu_options import SetuOptions
from .setu_record import Record
from .tooltip import Tooltip
from ..nonebot_plugin_utlie import config


class NoImageException(Exception):

    def __init__(self, tags: List[str], *args: object) -> None:
        super().__init__(*args)
        tags_text = "、".join('"{}"'.format(t) for t in tags)
        self.tooltip = Tooltip.NO_SETU_ERROR_TEXT_TEMPLATE % tags_text


class NoPainterException(Exception):

    def __init__(self, painter: str, *args: object) -> None:
        super().__init__(*args)
        self.tooltip = Tooltip.NO_PAINTER_ERROR_TEXT_TEMPLATE % painter


class RangeException(Exception):

    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        self.tooltip = Tooltip.RANGE_ERROR_TEXT


class ConnectTimeoutException(Exception):

    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        self.tooltip = Tooltip.CONNECT_TIMEOUT_ERROR_TEXT


class SetuAPI:

    def __init__(self, options: SetuOptions) -> None:
        self.options = options
        self.config = config
        self.setus: List[Dict[str, Any]] = []
        self.records = Record.get_records()

    def filter(self, pooling: Union[List[Dict[str, Any]], List[Any]], handle: Callable[..., Any]):
        amount = self.options.amount - self.options.quantity_completed
        amount = amount if len(pooling) >= amount else len(pooling)

        if self.options.matcher_rule == "count":
            filtered = [i for i in pooling if handle(i)]
            return [i for i in sample(filtered, amount)]

        else:
            _range = (self.options._range[0] - 1, self.options._range[1])
            if _range[0] > len(pooling) or _range[1] > len(pooling):
                raise RangeException()
            else:
                return [pooling[i] for i in range(*_range)]

    def format(self, pooling: Union[List[Dict[str, Any]], List[str]], handle: Callable[..., Any]):
        return [handle(setu) for setu in pooling]

    async def main(self):
        return self
