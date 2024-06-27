from Scripts.Managers import server_manager, data_manager

from nonebot import get_plugin_config, on_message, logger
from nonebot.adapters.onebot.v11 import GroupMessageEvent

from pydantic import BaseModel


class Config(BaseModel):
    command_start: list = None
    sync_message_groups: list = None


config = get_plugin_config(Config)
mapping = {'record': '转发', 'image': '图片', 'reply': '回复',
           'video': '视频', 'face': '表情', 'file': '文件'}


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
            plain_texts.append(segment.data['text'])
            continue
        elif segment.type == 'at':
            user = segment.data['qq']
            plain_texts.append(
                F'[@{data_manager.players.get(user, "Unknow")}]')
            continue
        plain_texts.append(F'[{mapping.get(segment.type, "未知类型")}]')
    plain_text = ' '.join(plain_texts)
    name = data_manager.players.get(str(event.user_id), '<Unknow>')
    server_manager.broadcast(F'[QQ] <{name}> {plain_text}', 'gray')
    logger.info(F'转发主群用户 {name} 消息 {plain_text} 到游戏内。')
