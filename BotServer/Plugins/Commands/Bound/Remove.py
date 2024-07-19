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
        if (len(args) == 0) or (len(args) > 2):
            await matcher.finish('参数错误，请检查语法是否正确')
        if len(args) == 1:
            args.append(str(event.user_id))
        if str(event.user_id) not in config.superusers:
            if not (args[1] == str(event.user_id)):
                await matcher.finish('你没有权限执行此命令！此ID不属于你')
    else:args = ["*", str(event.user_id)]
    message = bound_remove_handler(args)
    await matcher.finish(message)


def bound_remove_handler(args: list):
    player = args[0]
    user = args[1]
    if player == "*":
        if user not in data_manager.players:
            return F'用户 {user} 还没有绑定白名单！'
        for name in list(data_manager.players[user]):
            if not server_manager.execute(F'{config.whitelist_command} remove {name}'):
                return '当前没有已连接的服务器，删除失败！请连接后再次尝试。'
        data_manager.players.pop(user, None)
        data_manager.save()
        return F'用户 {user} -> all 已经从白名单中移除！'
    if user not in data_manager.players or player not in list(data_manager.players.get(user)):
        return F'用户 {user} 还没有绑定白名单 {player} ！'
    players = list(data_manager.players[user])
    if server_manager.execute(F'{config.whitelist_command} remove {player}'):
        players.remove(player)
        if not players:
            data_manager.players.pop(user, None)
        else:
            data_manager.players[user] = players
        data_manager.save()
        return F'用户 {user} -> {player} 已经从白名单中移除！'
    return '当前没有已连接的服务器，删除失败！请连接后再次尝试。'