from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.log import logger

from Scripts.Managers.Version import version_manager
from Scripts.Utils import Rules, turn_message

logger.debug('加载命令 About 完毕！')
matcher = on_command('about', force_whitespace=True, rule=Rules.command_rule)


@matcher.handle()
async def handle_group(event: GroupMessageEvent):
    message = turn_message(about_handler())
    await matcher.finish(message, at_sender=True)


def about_handler():
    yield F'当前版本为 {version_manager.version}，{"发现新版本，请及时更新！" if version_manager.check_update() else "已是最新版本！"}'
    yield '\n项目官网：https://qqbot.bugjump.xyz/'
    yield '项目地址 https://github.com/Minecraft-QQBot'
    yield '欢迎加入 QQ 交流群 962802248，对这个项目感兴趣不妨点个 Star 吧！'
