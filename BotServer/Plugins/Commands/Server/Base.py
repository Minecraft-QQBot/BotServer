from Scripts.Utils import turn_message, get_rule
from Scripts.Managers import server_manager, data_manager

from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent


matcher = on_command('server', force_whitespace=True, priority=10, rule=get_rule('server'))


@matcher.handle()
async def handle_group(event: GroupMessageEvent):
    message = turn_message(server_handler())
    await matcher.finish(message)


def server_handler():
    status = None
    for index, name in enumerate(data_manager.server_numbers):
        status = '在线' if server_manager.status.get(name) else '离线'
        yield F'({(index + 1):0>2}) [{name}] -> {status}'
    if not status:
        yield '当前没有已连接的服务器！请检查是否正确安装了 Mcdr 插件或启动服务器后再试。'
