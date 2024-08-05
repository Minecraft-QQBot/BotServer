from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message
from nonebot.log import logger
from nonebot.params import CommandArg

from Scripts.Managers import server_manager
from Scripts.Utils import get_permission, get_args, rule

logger.debug('命令 Mcdr 加载完毕！')
matcher = on_command('mcdr', force_whitespace=True, rule=rule)


@matcher.handle()
async def handle_group(event: GroupMessageEvent, args: Message = CommandArg()):
    if not get_permission(event):
        await matcher.finish('你没有权限执行此命令！')
    message = await mcdr_handler(get_args(args))
    await matcher.finish(message)


async def mcdr_handler(args: list):
    if len(args) <= 1:
        return '参数不正确！请查看语法后再试。'
    server_flag, *command = args
    command = ' '.join(command)
    if server_flag == '*':
        await server_manager.execute_mcdr(command)
        return '命令已发送到所有已连接的服务器！'
    if server := server_manager.get_server(server_flag):
        await server.send_mcdr_command(command)
        return F'命令发送到服务器 [{server.name}] 完毕！'
    return F'服务器 [{server_flag}] 不存在！'
