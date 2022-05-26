
import traceback
from asyncio import create_task, gather
from typing import AsyncGenerator, List
from nonebot import on_regex
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.params import CommandArg, RegexDict, Depends
from nonebot.adapters.onebot.v11 import Message, MessageEvent
from ..nonebot_plugin_utlie import config, on_command, Matcher
from .tooltip import Tooltip
from .event_state import EventState
from .session import Session
from .setu_options import SetuOptions
from .setu import Setu, SetuException

command_matcher = on_command("涩图", aliases={"色图", "瑟图", "setu"}, priority=5)
regex_matcher = on_regex(
    r"[来发](?P<amount>.*?)[张些点份](?P<tags>.*?)的?[涩色瑟]图", rule=to_me(), priority=5)


async def is_sending(matcher: Matcher):
    if EventState.is_block():
        await matcher.finish("正在发送图片，请不要重复请求")


def _Setu():
    async def _setu(matcher: Matcher, state: T_State):
        try:
            if "setu" in state:
                setu_generator = state["setu_generator"]
            else:
                setu_generator = await Setu(state["options"]).main()
                state["setu_generator"] = setu_generator

            state["setu"] = await setu_generator.__anext__()

        except SetuException as e:
            EventState.open()
            await matcher.finish(e.tooltip)

        except StopAsyncIteration as e:
            pass

        return state["setu"]

    return Depends(_setu, use_cache=False)


async def _setu_options(matcher: Matcher, state: T_State):
    options: SetuOptions = state["options"]
    if options.state == "failed":
        await matcher.finish(options.failed_message)

    return options


async def filtered_message(event: MessageEvent, state: T_State, setu: Setu = _Setu()):
    user_id = event.get_user_id()
    session: Session = state["session"]

    if user_id in config.superusers:
        return setu.messages

    if len(setu.messages) > session.limit:
        return setu.messages[:session.limit]
    else:
        return setu.messages


@command_matcher.handle()
@regex_matcher.handle()
async def _(
    matcher: Matcher,
    event: MessageEvent,
    state: T_State,
    is_sending: None = Depends(is_sending)):

    state["user_id"] = event.get_user_id()
    state["session"] = Session(state["user_id"])

    if state["user_id"] in config.superusers:
        return
    if state["session"].is_limited():
        await matcher.finish(Tooltip.LIMITED_TEXT)
    if state["session"].is_cooling():
        await matcher.finish(Tooltip.COOLING_TEXT)


@command_matcher.handle()
async def _(state: T_State, command_arg: Message = CommandArg()):
    state["options"] = SetuOptions(command_arg=command_arg)


@regex_matcher.handle()
async def _(state: T_State, regex_dict: dict = RegexDict()):
    state["options"] = SetuOptions(regex_dict=regex_dict)


@command_matcher.handle()
@regex_matcher.handle()
async def _(
    state: T_State,
    options: SetuOptions = Depends(_setu_options),
    setu: Setu = _Setu()):

    state["search_pattern"] = options.search_pattern
    EventState.block(state["user_id"])


@command_matcher.handle()
@regex_matcher.handle()
async def _(matcher: Matcher, state: T_State, setu: Setu = _Setu()):
    if state["search_pattern"] in ["tag", "ranking"]:
        state["skip"] = True
    elif state["search_pattern"] in ["painter"]:
        await matcher.send(state["setu"].image)


@command_matcher.got(key="skip")
async def _(matcher: Matcher, event: MessageEvent, state: T_State):
    result = [i.strip()
              for i in event.get_message().extract_plain_text().split(" ")]
    index, args = result[0], result[1:]

    if state["search_pattern"] in ["painter"]:
        setu: Setu = state["setu"]

        if index.isdigit() and 0 < int(index) <= len(setu.painters):
            state["skip"] = True
            state["index"] = int(index)

            EventState.block(state["user_id"])

            options: SetuOptions = state["options"]
            options.set_search_painter_options(args)

        elif index.isdigit() and int(index) == 0:
            await matcher.finish(Tooltip.SEARCH_SETU_INTERRUPT_TEXT)

        else:
            await matcher.reject_arg("skip")


@command_matcher.handle()
async def _(matcher: Matcher, state: T_State, options: SetuOptions = Depends(_setu_options)):
    if state["search_pattern"] in ["painter"]:
        setu_generator: AsyncGenerator = state["setu_generator"]
        try:
            await setu_generator.asend(state["index"] - 1)
        except SetuException as e:
            await matcher.finish(e.tooltip)


@command_matcher.handle()
@regex_matcher.handle()
async def _(matcher: Matcher, state: T_State):
    await matcher.send(Tooltip.SEARCH_SETU_LOADING_TEXT)


@command_matcher.handle()
@regex_matcher.handle()
async def _(
        matcher: Matcher,
        messages: List[Message] = Depends(filtered_message)):

    try:
        tasks = [create_task(matcher.send(msg)) for msg in messages]
        await gather(*tasks)
    except Exception as e:
        print(traceback.format_exc())
        EventState.open()
        await matcher.finish()


@command_matcher.handle()
@regex_matcher.handle()
async def _(matcher: Matcher, state: T_State):
    session: Session = state["session"]
    options: SetuOptions = state["options"]

    session.subtract(options.quantity_completed)
    session.save()

    EventState.open()

    await matcher.finish()
