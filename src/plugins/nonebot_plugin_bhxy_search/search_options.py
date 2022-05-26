
import re
from typing import Optional, Sequence
from .bhxy_types import equip_types, base_types, damage_types
from ..nonebot_plugin_utlie import canvert_str


class SearchOptions:

    def __init__(self, command_arg: str) -> None:
        self.command_arg = command_arg
        self.keywords = ""
        self.rarity = ""
        self.type = ""
        self.base_type = ""
        self.damage_type = ""
        self.series_text = ""

        if self.command_arg:
            self.__parse_command()

    def __parse_command(self):
        args = [i.strip() for i in self.command_arg.split(" ")]
        
        for arg in args:
            if arg[0] == "#" or arg[0] == "＃":
                for parse in [self.parse_rarity, self.parse_damage_type, self.parse_type, self.parse_series_text]:
                    if parse(arg[1:]):
                        break
            else:
                self.keywords = re.compile(arg, re.I)

    def parse_rarity(self, arg: str):
        if r := re.search("^(.*?)星", canvert_str(arg)):
            rarity = r.group(1)

            if rarity.isdigit() and 8 > int(rarity) > 0:
                self.rarity = rarity
                return True

    def parse_type(self, arg: str):
        if arg in equip_types.keys():
            self.type = equip_types[arg]
            return True

        for t in base_types:
            if arg in t:
                self.base_type = re.compile(arg)
                return True

    def parse_damage_type(self, arg: str):
        if arg in damage_types:
            self.damage_type = damage_types[arg]
            return True

    def parse_series_text(self, arg: str):
        self.series_text = arg

    def toDict(self, keyname: Optional[str]=None, ids: Optional[Sequence]=None):
        options = {}

        if keyname is not None:
            options[keyname] = self.keywords
        if ids is not None:
            options["id"] = re.compile("|".join(ids))
        if self.rarity:
            options["rarity"] = self.rarity
        if self.type:
            options["type"] = self.type
        if self.base_type:
            options["baseType"] = self.base_type
        if self.damage_type:
            options["damageType"] = self.damage_type
        if self.series_text:
            options["seriesText"] = self.series_text

        return options