from nonebot import on_message
from nonebot.adapters.onebot.v11 import GroupMessageEvent

from Scripts.Utils import Rules
from Scripts.Config import config
from nonebot.log import logger

logger.debug('加载 关键词回复 功能完毕！')
matcher = on_message(rule=Rules.message_rule, priority=15, block=False)


@matcher.handle()
async def watch_keywords(event: GroupMessageEvent):
    plain_text = event.get_plaintext()
    for reply_text, keywords in config.group_auto_reply_keywords.items():
        for keyword in keywords:
            if all(word in plain_text for word in keyword.split()):
                await matcher.finish(reply_text, at_sender=True)
