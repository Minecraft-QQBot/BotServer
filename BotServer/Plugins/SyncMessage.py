from nonebot import on_message
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.log import logger

from Scripts.Config import config
from Scripts.Managers import server_manager, data_manager
from Scripts.Utils import Rules, get_player_name, get_user_name

matcher = on_message(rule=Rules.message_rule)
mapping = {'record': '语音', 'image': '图片', 'reply': '回复', 'face': '表情', 'file': '文件'}


@matcher.handle()
async def sync_message(event: GroupMessageEvent):
    plain_text = event.get_plaintext()
    for start in config.command_start:
        if plain_text.startswith(start):
            return None
    plain_text = await turn_text(event)
    name = data_manager.players.get(str(event.user_id), [get_player_name(event.sender.card)])[0]
    await server_manager.broadcast('QQ', (name or event.sender.nickname), plain_text)
    logger.debug(F'转发主群用户 {event.sender.card} 消息 {plain_text} 到游戏内。')


async def turn_text(event: GroupMessageEvent):
    plain_texts = []
    for segment in event.get_message():
        if segment.type == 'text' and (text := segment.data['text']):
            plain_texts.append(text)
            continue
        if segment.type == 'at':
            user = str(segment.data['qq'])
            if player := data_manager.players.get(user):
                plain_texts.append(F'[@{player[0]}]')
                continue
            if player := get_player_name(await get_user_name(event.group_id, user)):
                plain_texts.append(F'[@{player}]')
                continue
            plain_texts.append(F'[@未知用户]')
            continue
        plain_texts.append(F'[{mapping.get(segment.type, "未知类型")}]')
    return ' '.join(plain_texts)
