from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent

from Scripts.Managers import data_manager
from Scripts.Utils import Rules, turn_message, get_permission

matcher = on_command('bound list', force_whitespace=True, block=True, priority=5, rule=Rules.command_rule)


@matcher.handle()
async def handle_group(event: GroupMessageEvent):
    if not get_permission(event):
        await matcher.finish('你没有权限执行此命令！')
    message = turn_message(bound_list_handler())
    await matcher.finish(message)


def bound_list_handler():
    if data_manager.players:
        yield '白名单列表：'
        for user, player in data_manager.players.items():
            yield F'  {user} -> {"、".join(player)}'
        return None
    yield '当前没有绑定任何玩家！'
