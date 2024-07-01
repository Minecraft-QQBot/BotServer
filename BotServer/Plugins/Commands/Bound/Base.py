from Scripts.Utils import get_rule
from Scripts.Managers import data_manager, server_manager

from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message


matcher = on_command('bound', force_whitespace=True, priority=10, rule=get_rule('bound'))


@matcher.handle()
async def handle_group(event: GroupMessageEvent, args: Message = CommandArg()):
    if player := args.extract_plain_text():
        await matcher.finish(bound_handle(event.user_id, player))
    if (user := event.user_id) not in data_manager.players.keys():
        await matcher.finish('你还没有绑定白名单，请先绑定后再试。')
    await matcher.finish(F'用户 {user} 你已绑定白名单到 {data_manager.players[user]} 玩家。')


def bound_handle(user: int, player: str):
    if user in data_manager.players.keys():
        return '你已经绑定了白名单！请先解绑后尝试。'
    if player in data_manager.players.items():
        return '此玩家名称已经绑定过了，请换一个名称！'
    if server_manager.execute(F'whitelist add {player}'):
        data_manager.players.setdefault(user, player)
        return F'用户 {user} 已成功绑定白名单到 {player} 玩家。'
    return '当前没有已连接的服务器，绑定失败！请联系管理员连接后再试。'
