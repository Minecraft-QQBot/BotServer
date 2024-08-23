from datetime import datetime

from nonebot import on_notice
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import (
    GroupDecreaseNoticeEvent, GroupIncreaseNoticeEvent, PokeNotifyEvent, GroupMessageEvent
)

from Scripts.Network import request
from Scripts.Config import config
from Scripts.Managers import data_manager, server_manager
from Scripts.Utils import Rules, turn_message

matcher = on_notice(rule=Rules.message_rule)
week_mapping = ('一', '二', '三', '四', '五', '六', '日')


@matcher.handle()
async def watch_decrease(event: GroupDecreaseNoticeEvent):
    logger.info(F'检测到用户 {event.user_id} 离开了群聊！')
    if player := data_manager.remove_player(str(event.user_id)):
        await server_manager.execute(F'{config.whitelist_command} remove {player}')
        await matcher.finish(F'用户 {event.user_id} 离开了群聊，自动从白名单中移除 {"、".join(player)} 玩家。')


@matcher.handle()
async def watch_increase(event: GroupIncreaseNoticeEvent):
    await matcher.finish('欢迎加入群聊！请仔细阅读群聊公告，并按照要求进行操作。', at_sender=True)


@matcher.handle()
async def watch_keywords(event: GroupMessageEvent):
    if not config.auto_reply:
        return None
    plain_text = event.get_plaintext()
    for reply_text, keywords in config.auto_reply_keywords.items():
        for keyword in keywords:
            if all(word in plain_text for word in keyword.split()):
                await matcher.finish(reply_text, at_sender=True)


@matcher.handle()
async def watch_poke(event: PokeNotifyEvent):
    if not event.is_tome():
        return None
    sentence = await request('https://v1.jinrishici.com/all.json')
    message = turn_message(poke_handler(sentence))
    await matcher.finish(message)


def poke_handler(sentence):
    now = datetime.now()
    yield F'{now.strftime("%Y-%m-%d")} 星期{week_mapping[now.weekday()]}  {now.strftime("%H:%M:%S")}'
    if sentence is None:
        yield F'\n「{sentence["content"]}」'
        yield F'               —— {sentence["author"]}《{sentence["origin"]}》'
