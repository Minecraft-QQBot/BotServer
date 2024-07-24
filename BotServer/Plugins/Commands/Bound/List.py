from Scripts.Config import config
from Scripts.Managers import data_manager
from Scripts.Utils import turn_message, rule

from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent


matcher = on_command('bound list', force_whitespace=True, block=True, priority=5, rule=rule)


@matcher.handle()
async def handle_group(event: GroupMessageEvent):
    if str(event.user_id) not in config.superusers:
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
