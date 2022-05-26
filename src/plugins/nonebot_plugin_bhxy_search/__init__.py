
from nonebot.params import CommandArg, Depends
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import Message, MessageEvent, MessageSegment
from pathlib import Path
from ..nonebot_plugin_utlie import on_command, Matcher
from .associate import Associate, RepeatException
from .search_options import SearchOptions
from .search_equips import SearchEquips
from .draw import draw_image

search_matcher = on_command(
    "查询",
    aliases={"查询装备", "搜索装备", "搜索", "装备"},
    priority=5,
    state={"append_associated_ready": False, "delete_associated_ready": False}
)


async def select_handle(matcher: Matcher, state: T_State, event: MessageEvent):
    # 选择装备发送图鉴图片
    args = event.get_plaintext().split()

    if args[0].isdigit():

        if int(args[0]) <= 0:
            await matcher.finish("已结束此次查询")

        elif int(args[0]) <= len(state["equips"]):
            index = int(args[0]) - 1
            equip = state["equips"][index][0]
            img_length = len(equip['img'])
            img_name = (('00' if img_length < 2 else '0')
                        if img_length < 3 else '') + equip['img']

            plugin_name = matcher.plugin_name if matcher.plugin_name is not None else ""
            img_path = Path("./src/plugins/" + plugin_name + "/image/")
            img = MessageSegment.image(img_path.joinpath(img_name + ".png"))

            await matcher.send(img)


async def associate_handle(state: T_State, event: MessageEvent):
    # 获取关联所需的参数并保存至state
    args = event.get_plaintext().split()

    if args[0] in ["关联", "取消关联"] and len(args) > 2:
        state["user_id"] = event.get_user_id()
        state["keywords"] = [i for i in args[1:] if not i.isdigit()]
        index = [i for i in args if i.isdigit()]
        state["selected"] = [v[0] for i, v in enumerate(state["equips"]) if str(i + 1) in index]
        state["associate_equips"] = [
            (i["id"], i["rarity"], i["title"]) for i in state["selected"]]


async def delete_associated_handle(matcher: Matcher, state: T_State, event: MessageEvent):
    # 删除与关键词关联的装备
    args = event.get_plaintext().split()

    if args[0] == "取消关联" and len(args) > 2:
        state["delete_associated_ready"] = True

        await matcher.send("是否确定将以下装备从关键词“{}”中取消关联\n\n{}\n\n确定\t\t取消".format(
            '、'.join(state['keywords']),
            '  '.join([f"[{i['rarity']}★]{i['title']}" for i in state["selected"]])
        ))

    elif state["delete_associated_ready"]:
        if args[0] == "确定":
            try:
                Associate.delete(
                    state["keywords"], state["associate_equips"], state["user_id"])

                await matcher.send("已将选定的{}件装备从关键词“{}”中取消关联".format(
                    str(len(state["associate_equips"])),
                    "、".join(state['keywords'])
                ))

            except RepeatException as e:
                await matcher.send("以下装备已经关联到此关键词了，请不要重复添加 \n\n{}".format(
                    '  '.join(
                        [f"[{i['rarity']}★]{i['title']}" for i in e.repeated])
                ))

        elif args[0] == "取消":
            await matcher.send("已取消")

        state["delete_associated_ready"] = False


async def append_associated_handle(matcher: Matcher, state: T_State, event: MessageEvent):
    # 添加装备关联到关键词
    args = event.get_plaintext().split()

    if args[0] == "关联" and len(args) > 2:
        state["append_associated_ready"] = True

        await matcher.send("是否确定将以下装备关联到关键词“{}”\n\n{}\n\n确定\t\t取消".format(
            '、'.join(state['keywords']),
            '  '.join([f"[{i['rarity']}★]{i['title']}" for i in state["selected"]])
        ))

    elif state["append_associated_ready"]:
        if args[0] == "确定":
            try:
                Associate.append(
                    state["keywords"], state["associate_equips"], state["user_id"])

                await matcher.send("已将选定的{}件装备关联到关键词“{}”中".format(
                    str(len(state["associate_equips"])),
                    "、".join(state['keywords'])
                ))
            except RepeatException as e:
                await matcher.send("以下装备已经关联到此关键词了，请不要重复添加 \n\n{}".format(
                    '  '.join(
                        [f"[{i['rarity']}★]{i['title']}" for i in e.repeated])
                ))

        elif args[0] == "取消":
            await matcher.send("已取消")

        state["append_associated_ready"] = False


@search_matcher.handle()
async def _(matcher: Matcher, state: T_State, command_arg: Message = CommandArg()):
    options = SearchOptions(command_arg.extract_plain_text())

    if result := await SearchEquips.search(options):
        image_bytes = draw_image(result, len(result))
        image = MessageSegment.image(image_bytes)
        await matcher.send(image)

        state["equips"] = result

    else:
        await matcher.finish("没有查找到有关的装备")


@search_matcher.receive()
async def _(
    matcher: Matcher,
    select: None = Depends(select_handle),
    associate: None = Depends(associate_handle),
    append: None = Depends(append_associated_handle),
    delete: None = Depends(delete_associated_handle)
):
    await matcher.reject()
