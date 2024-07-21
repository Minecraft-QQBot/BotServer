from Scripts.Config import config
from Scripts.Managers import server_manager, data_manager

from nonebot import on_message
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from Scripts.Utils import get_player_name, get_user_name


mapping = {'record': '聊天记录', 'image': '图片', 'reply': '回复', 'face': '表情', 'file': '文件'}


@on_message
async def sync_message(event: GroupMessageEvent):
    if event.group_id not in config.message_groups:
        return None
    plain_text = event.get_plaintext()
    for start in config.command_start:
        if plain_text.startswith(start):
            return None
    plain_texts = []
    for segment in event.get_message():
        if segment.type == 'text':
            if text := segment.data['text']:
                plain_texts.append(text)
            continue
        elif segment.type == 'at':
            user_id = str(segment.data['qq'])
            if player := data_manager.players.get(user_id, get_player_name(await get_user_name(event.group_id, event.user_id))):
                plain_texts.append(F'[@{player}]')
                continue
            plain_texts.append(F'[@未知用户]')
            continue
        plain_texts.append(F'[{mapping.get(segment.type, "未知类型")}]')
    plain_text = ' '.join(plain_texts)
    name = data_manager.players.get(str(event.user_id), get_player_name(event.sender.card))
    server_manager.broadcast('QQ', name, plain_text)
    logger.debug(F'转发主群用户 {event.sender.card} 消息 {plain_text} 到游戏内。')