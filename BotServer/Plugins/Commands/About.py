# 导入必要的模块和函数
from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.log import logger

# 导入自定义的工具和管理器
from Scripts.Utils import Rules, turn_message
from Scripts.Managers.Version import version_manager

# 记录关于命令的加载日志
logger.debug('加载命令 About 完毕！')

# 定义关于命令的匹配器，使用自定义规则进行消息匹配
matcher = on_command('about', force_whitespace=True, rule=Rules.command_rule)


@matcher.handle()
async def handle_group(event: GroupMessageEvent):
    """
    处理群组中的关于命令。

    参数:
    - event: 群消息事件

    该函数将调用 about_handler 函数生成关于信息，并使用 matcher.finish 方法回复消息。
    """
    message = turn_message(about_handler())
    await matcher.finish(message, at_sender=True)


def about_handler():
    """
    关于信息处理器。

    该函数生成关于信息的多行文本。

    返回:
    - 版本信息和项目相关链接的多行字符串。
    """
    yield F'当前版本为 {version_manager.version}，{"发现新版本，请及时更新！" if version_manager.check_update() else "已是最新版本！"}'
    yield '\n项目官网：https://qqbot.bugjump.xyz/'
    yield '项目地址 https://github.com/Minecraft-QQBot'
    yield '欢迎加入 QQ 交流群 962802248，对这个项目感兴趣不妨点个 Star 吧！'
