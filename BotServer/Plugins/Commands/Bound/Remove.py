from Scripts.Config import config
from Scripts.Utils import get_args, rule
from Scripts.Managers import data_manager, server_manager

from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message


matcher = on_command('bound remove', force_whitespace=True, block=True, priority=5, rule=rule)


@matcher.handle()
async def handle_group(event: GroupMessageEvent, args: Message = CommandArg()):
    if args := get_args(args):
        if str(event.user_id) not in config.superusers:
            await matcher.finish('你没有权限执行此命令！')
        message = bound_remove_handler(args)
        await matcher.finish(message)
    message = bound_remove_handler([str(event.user_id)])
    await matcher.finish(message)


def bound_remove_handler(args: list):
    if len(args) != 1:
        return '参数错误！请检查语法是否正确。'
    if not (user := args[0]).isdigit():
        return '参数错误！删除绑定的 QQ 号格式错误。'
    if not (player := data_manager.players.pop(user, None)):
        return F'用户 {user} 还没有绑定白名单！'
    if server_manager.execute(F'{config.whitelist_command} remove {player}'):
        data_manager.save()
        return F'用户 {user} 已经从白名单中移除！'
    return '当前没有已连接的服务器，删除失败！请连接后再次尝试。'
