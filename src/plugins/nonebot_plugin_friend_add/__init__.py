from nonebot import on_request
from nonebot.adapters.onebot.v11 import Bot, FriendRequestEvent
from ..nonebot_plugin_utlie import config

req_matcher = on_request()


@req_matcher.handle()
async def _(bot:Bot, event: FriendRequestEvent):
    user_id = event.user_id
    flag = event.flag

    result = await bot.get_group_member_list(group_id=config.group_id)
    ids = [i["user_id"] for i in result]

    if user_id in ids:
        await bot.set_friend_add_request(flag=flag, approve=True)