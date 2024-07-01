from Scripts.Utils import get_rule, get_args
from Scripts.Managers import data_manager, server_manager

from nonebot.params import CommandArg
from nonebot import get_plugin_config, on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message

from pydantic import BaseModel


class Config(BaseModel):
    superusers: list = None


config = get_plugin_config(Config)
matcher = on_command('bound remove', force_whitespace=True, block=True, priority=5, rule=get_rule('bound'))


@matcher.handle()
async def handle_group(event: GroupMessageEvent, args: Message = CommandArg()):
    if args := get_args(args):
        if str(event.user_id) not in config.superusers:
            await matcher.finish('你没有权限执行此命令！')
        message = bound_remove_handle(args)
        await matcher.finish(message)
    message = bound_remove_handle([str(event.user_id)])
    await matcher.finish(message)


def bound_remove_handle(args: list):
    if len(args) != 1:
        return '参数错误！请检查语法是否正确。'
    if (user := args[0]) not in data_manager.players.keys():
        return F'用户 {user} 还没有绑定白名单！'
    player = data_manager.players[user]
    if server_manager.execute(F'whitelist remove {player}'):
        data_manager.players.pop(user)
        return F'用户 {user} 已经从白名单中移除！'
    return '当前没有已连接的服务器，删除失败！请连接后再次尝试。'
