from Scripts.Config import config
from Scripts.Utils import check_player, get_rule, get_args
from Scripts.Managers import server_manager, data_manager

from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message


matcher = on_command('bound append', force_whitespace=True, block=True, priority=5, rule=get_rule('bound'))


@matcher.handle()
async def handle_group(event: GroupMessageEvent, args: Message = CommandArg()):
    if str(event.user_id) not in config.superusers:
        await matcher.finish('你没有权限执行此命令！')
    args = get_args(args)
    message = bound_append_handler(args)
    await matcher.finish(message)


def bound_append_handler(args: list):
    if len(args) != 2:
        return '参数错误！请检查语法是否正确。'
    player, user = args
    if not user.isdigit():
        return '参数错误！绑定的 QQ 号格式错误。'
    if not check_player(player):
        return '玩家名称非法！玩家名称只能包含字母、数字、下划线且长度不超过 16 个字符。'
    # if user in data_manager.players:
    #     return F'用户 {user} 已经绑定了白名单！请先解绑后尝试。'
    for players in data_manager.players.values():
        if player in list(players):
            return '此玩家名称已经绑定过了，请换一个名称！'
    if server_manager.execute(F'{config.whitelist_command} add {player}'):
        if not (players := data_manager.players.get(user)):
            players = []
        players.append(player)
        data_manager.players.setdefault(user, players)
        data_manager.save()
        return F'用户 {user} 已绑定白名单到 {player} 玩家。'
    return '当前没有已链接的服务器，绑定失败！请连接后再试。'
