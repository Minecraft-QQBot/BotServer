from Scripts.Managers import data_manager
from Scripts.Utils import get_username, get_rule, turn_message

from nonebot import get_plugin_config, on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent

from pydantic import BaseModel


class Config(BaseModel):
    superusers: list = None


config = get_plugin_config(Config)
matcher = on_command('bound list', force_whitespace=True, block=True, priority=5, rule=get_rule('bound'))


@matcher.handle()
async def handle_group(event: GroupMessageEvent):
    if str(event.user_id) not in config.superusers:
        await matcher.finish('你没有权限执行此命令！')
    message = turn_message(bound_list_handle())
    await matcher.finish(message)


def bound_list_handle():
    if data_manager.players:
        for user, player in data_manager.players.items():
            yield F'  {user} -> {player}'
        return None
    yield '当前没有绑定任何玩家！'
