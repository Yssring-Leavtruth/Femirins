
import re
from typing import List, Dict, Union
from nonebot import require, get_driver
from nonebot.adapters.onebot.v11 import Message
from .tooltip import Tooltip
from ..nonebot_plugin_utlie import canvert_str, config


class SetuOptions:

    def __init__(
            self,
            command_arg: Union[Message, None] = None,
            regex_dict: Union[Dict[str, str], None] = None) -> None:

        self.state: str = "unfinished"
        self.failed_message: str = ""
        self.amount: int = 1
        self.quantity_completed: int = 0
        self.setu_size = config.setu_size
        self.tags: List[str] = []
        self._range: tuple = (1, 2)
        self.painter: str = ""
        self.ranking_pattern: str = "日榜"
        self.matcher_type: str = "command"
        self.matcher_rule: str = "count"
        self.search_pattern: str = "tag"
        self.raw_content: Union[str, Dict[str, str]] = ""
        self.__search_pattern_examples: Dict[str, str] = {
            "画师": "painter",
            "排行": "ranking",
            "排行榜": "ranking"
        }
        self.__ranking_pattern_examples: Dict[str, str] = {
            '日榜': 'daily',
            '周榜': 'weekly',
            '月榜': 'monthly'
        }

        if regex_dict is not None:
            self.matcher_type = "regex"
            self.raw_content = regex_dict
        elif command_arg is not None:
            self.matcher_type = "command"
            self.raw_content = command_arg.extract_plain_text()

        self.__extract_options()

        if self.state == "unfinished":
            self.state = "finished"
            self.__verify()

    def set_search_painter_options(self, args):
        self.raw_content = "".join(args)
        self.__parse_command()
        self.__verify()

    def __verify(self):
        if self.matcher_rule == "range" and self._range[1] - self._range[0] < 1:
                self.__set_state_failed(Tooltip.RANGE_ERROR_TEXT)

        elif self.amount < 1:
            self.__set_state_failed(Tooltip.BELOW_MINIMUM_TEXT)

        elif self.amount > config.setu_maximum:
            self.__set_state_failed(
                Tooltip.EXCEED_MAXIMUM_TEXT_TEMPLATE % config.setu_maximum)

    def __set_state_failed(self, message: str):
        self.state = "failed"
        self.failed_message = message

    def __extract_options(self):

        if self.matcher_type == "command":
            return self.__parse_command()
        else:
            return self.__parse_regex()

    def __parse_regex(self):

        if isinstance(self.raw_content, dict):
            for i in self.raw_content.values():
                self.__set_arguments(i)

    def __parse_command(self):

        if self.raw_content and isinstance(self.raw_content, str):
            raw_args = [i.strip() for i in self.raw_content.split(" ")]

            for i in raw_args:
                if i[0] == "#" or i[0] == "＃":
                    self.__set_search_pattern(i[1:])

                else:
                    self.__set_arguments(i)

    def __set_search_pattern(self, _string: str):

        if _string in self.__search_pattern_examples.keys():
            self.search_pattern = self.__search_pattern_examples[_string]

        else:
            self.__set_state_failed(
                Tooltip.SEARCH_PATTERN_ERROR_TEXT_TEMPLATE % _string)

    def __set_arguments(self, _string):

        if r := re.findall(r"^(\d+)$", _string):
            self.amount = int(r[0])

        elif r := re.findall(r"^([零一二三四五六七八九十]+)$", _string):
            self.amount = int(canvert_str(_string))

        elif r := re.findall(r"^(\d+)~(\d+)$", _string):
            self.matcher_rule = "range"
            self._range = (int(r[0][0]), int(r[0][1]))
            self.amount = self._range[1] - self._range[0] + 1

        else:
            if self.search_pattern == "painter":
                self.__set_painter(_string)

            elif self.search_pattern == "ranking":
                self.__set_ranking_pattern(_string)

            elif self.search_pattern == "tag":
                self.__set_tags(_string)

    def __set_painter(self, _string: str):
        self.painter = _string

    def __set_ranking_pattern(self, _string: str):

        if _string in self.__ranking_pattern_examples.keys():
            self.ranking_pattern = self.__ranking_pattern_examples[_string]

        else:
            self.__set_state_failed(Tooltip.RANKING_ARGUMENTS_ERROR_TEXT)

    def __set_tags(self, _string: str):

        if "," in _string:
            self.tags += _string.split(",")

        elif "，" in _string:
            self.tags += _string.split("，")

        elif "、" in _string:
            self.tags += _string.split("、")

        else:
            self.tags.append(_string)
