from Scripts.Utils import get_rule, get_args
from Scripts.Managers import server_manager, data_manager

from nonebot.params import CommandArg
from nonebot import get_plugin_config, on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message

from pydantic import BaseModel


class Config(BaseModel):
    superusers: list = None


config = get_plugin_config(Config)
matcher = on_command('command', force_whitespace=True, rule=get_rule('command'))


@matcher.handle()
async def handle_group(event: GroupMessageEvent, args: Message = CommandArg()):
    if str(event.user_id) not in config.superusers:
        await matcher.finish('你没有权限执行此命令！')
    args = get_args(args)
    message = command_handle(args)
    await matcher.finish(message)


def command_handle(args: list):
    if len(args) <= 2:
        return '参数错误！请检查语法是否正确。'
    server, * command = args
    command = ' '.join(command)
    server = (None if server == '*' else server)
    if server_manager.execute(command, server):
        return '命令已发送到服务器！'
    return F'服务器 [{server}] 不存在，请检查编号或名称是否输入正确。'

    