from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.log import logger

from Version import __version__
from Scripts.Utils import turn_message, rule

logger.debug('加载命令 About 完毕！')
matcher = on_command('about', force_whitespace=True, rule=rule)


@matcher.handle()
async def handle_group(event: GroupMessageEvent):
    message = turn_message(about_handler())
    await matcher.finish(message, at_sender=True)


def about_handler():
    yield F'当前版本：{__version__}'
    yield '项目地址：https://github.com/Minecraft-QQBot\n'
    yield '欢迎加入 QQ 群 962802248 交流，对这个项目感兴趣不妨点个 Star 吧！'
