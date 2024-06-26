from Scripts.Managers import server_manager

from nonebot import get_plugin_config, on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message

from pydantic import BaseModel


class Config(BaseModel):
    command_groups: list = None
    command_enabled: list = None


config = get_plugin_config(Config)
matcher = on_command('server', force_whitespace=True)


@matcher.handle()
async def handle_group(event: GroupMessageEvent):
    if not (('server' in config.command_enabled) or (event.group_id in config.command_groups)):
        await matcher.finish()
    lines = tuple(server_handle())
    message = Message('\n'.join(lines))
    await matcher.finish(message)


def server_handle():
    status = None
    for index, name in enumerate(server_manager.numbers):
        status = '在线' if server_manager.status.get(name) else '离线'
        yield F'编号为 {index} 的服务器 [{name}] {status}'
    if not status: yield '当前没有已连接的服务器！'
