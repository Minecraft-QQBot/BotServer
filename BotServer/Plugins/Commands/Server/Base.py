from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageEvent

from Scripts.Managers import server_manager, data_manager
from Scripts.Utils import turn_message, rule

matcher = on_command('server', force_whitespace=True, priority=10, rule=rule)


@matcher.handle()
async def handle_group(event: MessageEvent):
    message = turn_message(server_handler())
    await matcher.finish(message)


def server_handler():
    status = None
    for index, name in enumerate(data_manager.servers):
        if server := server_manager.servers.get(name):
            status = '在线' if server.status else '离线'
            yield F'({(index + 1):0>2}) [{name}] -> {status}'
            continue
        yield F'({(index + 1):0>2}) [{name}] -> 离线'
    if not status:
        yield '当前没有已连接的服务器！请检查是否正确安装了插件或重启服务器后再试。'
