from Scripts.Config import config
from Scripts.Utils import get_rule, get_args
from Scripts.Managers import data_manager, server_manager

from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message


matcher = on_command('bound remove', force_whitespace=True, block=True, priority=5, rule=get_rule('bound'))


@matcher.handle()
async def handle_group(event: GroupMessageEvent, args: Message = CommandArg()):
    if args := get_args(args):
        if len(args) == 1:
            args.append(str(event.user_id))
        if str(event.user_id) not in config.superusers:
            if args[0] in data_manager.players[str(event.user_id)]:
                bound_remove_handler(args)
            await matcher.finish('你没有权限执行此命令！,此ID不属于你')
        message = bound_remove_handler(args)
        await matcher.finish(message)
    args = ["*", event.user_id]
    message = bound_remove_handler(args)
    await matcher.finish(message)


def bound_remove_handler(args: list):
    if len(args) > 2:
        return '参数错误！请检查语法是否正确。'
    if args[0] == "*":
        try:
            for player in list(data_manager.players[args[1]]):
                if not server_manager.execute(f'{config.whitelist_command} remove {player}'):
                    return '当前没有已连接的服务器，删除失败！请连接后再次尝试。'
            data_manager.players.pop(args[1]), None
            data_manager.save()
            return F'用户 {args[1]} -> all 已经从白名单中移除！'
        except (KeyError,ValueError):
            return F'用户 {args[1]} 还没有绑定白名单！'
    try:
        players = list(data_manager.players[args[1]])
        if server_manager.execute(F'{config.whitelist_command} remove {args[0]}'):
            players.remove(args[0])
            data_manager.players[args[1]] = players
            data_manager.save()
            return F'用户 {args[1]} -> {args[0]}已经从白名单中移除！'
        return '当前没有已连接的服务器，删除失败！请连接后再次尝试。'
    except (KeyError,ValueError):
        return F'用户 {args[1]} 还没有绑定白名单 {args[0]} ！'  