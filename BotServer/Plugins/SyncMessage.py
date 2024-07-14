import re
from Scripts.Config import config
from Scripts.Managers import server_manager, data_manager

from nonebot import on_message, get_bot
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import GroupMessageEvent


mapping = {'record': '聊天记录', 'image': '图片', 'reply': '回复', 'face': '表情', 'file': '文件'}


@on_message
async def sync_message(event: GroupMessageEvent):
    if event.group_id not in config.sync_message_groups:
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
            user = str(segment.data['qq'])
            plain_texts.append(F"[@{data_manager.players.get(user, await get_group_card(user))}]")
            continue
        plain_texts.append(F'[{mapping.get(segment.type, "未知类型")}]')
    plain_text = ' '.join(plain_texts)
    name = data_manager.players.get(str(event.user_id), await check_player(event.sender.card))
    server_manager.broadcast(F'[QQ] <{name}> {plain_text}', 'gray')
    logger.debug(F'转发主群用户 {name} 消息 {plain_text} 到游戏内。')

async def get_group_card(user_id):
    bot = get_bot()
    req = await bot.call_api('get_group_member_info', group_id = config.sync_message_groups, user_id = user_id)
    return await check_player(req['card'])
    
    
async def check_player(player):
    try: 
        return re.findall(r'[a-zA-Z0-9_]+', player)[0]
    except IndexError:
        return "未知用户"