from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageEvent, Message
from nonebot.params import CommandArg

from Scripts.Managers import server_manager, data_manager
from Scripts.Utils import Rules, get_permission

server_remove_matcher = on_command('server remove', force_whitespace=True, block=True, priority=5, rule=Rules.command_rule)


@server_remove_matcher.handle()
async def handle_group(event: MessageEvent, args: Message = CommandArg()):
    if not get_permission(event):
        await server_remove_matcher.finish('你没有权限执行此命令！')
    if server_flag := args.extract_plain_text().strip():
        if name := parse_flag(server_flag):
            data_manager.remove_server(name)
            if server := server_manager.servers.pop(name, None):
                await server.disconnect()
            await server_remove_matcher.finish(F'已成功删除服务器 [{name}] ！')
        await server_remove_matcher.finish(F'未找到服务器 [{server_flag}] ！请检查输入的内容是否为编号或名称。')
    await server_remove_matcher.finish('请输入参数！')


def parse_flag(server_flag: str):
    if server_flag.isdigit():
        server_flag = int(server_flag)
        if server_flag > len(data_manager.servers):
            return None
        return data_manager.servers[server_flag - 1]
    if server_flag in data_manager.servers:
        return server_flag
