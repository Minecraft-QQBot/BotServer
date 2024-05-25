from nonebot import on_message, logger
from nonebot.adapters.onebot.v11 import GroupMessageEvent

from Config import config
from Minecraft import server_manager


@on_message
async def sync_message(event: GroupMessageEvent):
    if event.group_id != config.main_group:
        return None
    message = event.get_plaintext()
    for start in config.command_start:
        if message.startswith(start):
            return None
    name = config.players.get(str(event.user_id))
    server_manager.say(F'[QQ] <{name}> {message}', 'gray')
    logger.info(F'转发主群用户 {name} 消息 {message} 到游戏内。')
