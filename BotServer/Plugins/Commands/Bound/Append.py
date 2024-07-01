from Scripts.Utils import get_rule, get_args
from Scripts.Managers import server_manager, data_manager

from nonebot.params import CommandArg
from nonebot import get_plugin_config, on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message

from pydantic import BaseModel


class Config(BaseModel):
    superusers: list = None


config = get_plugin_config(Config)
matcher = on_command('bound append', force_whitespace=True, block=True, priority=5, rule=get_rule('bound'))


@matcher.handle()
async def handle_group(event: GroupMessageEvent, args: Message = CommandArg()):
    if str(event.user_id) not in config.superusers:
        await matcher.finish('你没有权限执行此命令！')
    args = get_args(args)
    message = bound_append_handle(args)
    await matcher.finish(message)


def bound_append_handle(args: list):
    if len(args) != 2:
        return '参数错误！请检查语法是否正确。'
    user, player = args
    if user in data_manager.players.keys():
        return F'用户 {user} 已经绑定了白名单！请先解绑后尝试。'
    if player in data_manager.players.items():
        return '此玩家名称已经绑定过了，请换一个名称！'
    if server_manager.execute(F'whitelist add {player}'):
        data_manager.players.setdefault(user, player)
        return F'用户 {user} 已绑定白名单到 {player} 玩家。'
    return '当前没有已链接的服务器，绑定失败！请连接后再试。'

    