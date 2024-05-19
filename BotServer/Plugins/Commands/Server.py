from Config import config
from Minecraft import server_manager

from nonebot import on_command
from nonebot.adapters.onebot.v11 import PrivateMessageEvent, GroupMessageEvent, Message


matcher = on_command('server', force_whitespace=True)


@matcher.handle()
async def handle_group(event: GroupMessageEvent):
    if event.group_id != config.main_group:
        await matcher.finish()
    lines = tuple(server_handle())
    message = Message('\n'.join(lines))
    await matcher.finish(message)


@matcher.handle()
async def handle_private(event: PrivateMessageEvent):
    lines = tuple(server_handle())
    message = Message('\n'.join(lines))
    await matcher.finish(message)


def server_handle():
    for index, name in enumerate(server_manager.numbers):
        status = "在线" if server_manager.status.get(name) else "离线"
        yield F'编号为 ({index}) 的服务器 [{name}] 状态： {status} 。'
