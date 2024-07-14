from Scripts.Config import config
from Scripts.Utils import check_player, get_rule
from Scripts.Managers import data_manager, server_manager

from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message


matcher = on_command('bound', force_whitespace=True, priority=10, rule=get_rule('bound'))


@matcher.handle()
async def handle_group(event: GroupMessageEvent, args: Message = CommandArg()):
    if player := args.extract_plain_text().strip():
        await matcher.finish(bound_handler(str(event.user_id), player))
    if (user := str(event.user_id)) not in data_manager.players.keys():
        await matcher.finish('你还没有绑定白名单，请先绑定后再试。')
    await matcher.finish(F'用户 {user} 你已绑定白名单到 {data_manager.players[user]} 玩家。')


def bound_handler(user: str, player: str):
    if not check_player(player):
        return '此玩家名称非法！玩家名称应只包含字母、数字、下划线且长度不超过 16 个字符。'
    if user in data_manager.players:
        return '你已经绑定了白名单！请先解绑后尝试。'
    if player in data_manager.players.values():
        return '此玩家名称已经绑定过了，请换一个名称！'
    if server_manager.execute(F'{config.whitelist_command} add {player}'):
        data_manager.players.setdefault(user, player)
        data_manager.save()
        return F'用户 {user} 已成功绑定白名单到 {player} 玩家。'
    return '当前没有已连接的服务器，绑定失败！请联系管理员连接后再试。'
