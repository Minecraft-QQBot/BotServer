# 导入必要的模块和函数
from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message
from nonebot.log import logger
from nonebot.params import CommandArg

# 导入自定义模块和函数
from Scripts.Config import config
from Scripts.Managers import data_manager
from Scripts.Utils import Rules, turn_message

# 初始化日志记录器
logger.debug('加载命令 Help 完毕！')

# 定义帮助命令的匹配器
matcher = on_command('help', force_whitespace=True, rule=Rules.command_rule)


# 定义帮助命令的处理函数
@matcher.handle()
async def handle_group(event: GroupMessageEvent, args: Message = CommandArg()):
    """
    处理帮助命令的函数。

    参数:
    - event: 群聊消息事件
    - args: 命令参数
    """
    # 如果提供了命令名称
    if name := args.extract_plain_text().strip():
        message = turn_message(detailed_handler(name))
        await matcher.finish(message)
    # 如果没有提供命令名称
    message = turn_message(help_handler())
    await matcher.finish(message)


# 定义命令列表帮助函数
def help_handler():
    """
    返回所有可用命令的列表。

    该函数是一个生成器，用于逐条生成命令列表的文本。
    """
    yield '命令列表：'
    # 遍历所有启用的命令
    for name in config.command_enabled:
        info = data_manager.commands[name]
        yield F'  {name} — {data_manager.commands[name]["description"]}'
        # 如果命令有子命令
        if children := info.get('children'):
            for child_name, child_info in children.items():
                yield F'  +-- {name} {child_name} — {child_info["description"]}'
    # 提醒必填和可选参数的表示方法
    yield '\n注：<name> 代表必填的参数，<*name> 代表此参数可选。对于所有需要输入 QQ 号的指令，可以通过 @ 此用户来代替输入的 QQ 号。'


# 定义详细帮助信息处理函数
def detailed_handler(name: str):
    """
    返回指定命令的详细信息。

    参数:
    - name: 命令名称

    该函数是一个生成器，用于逐条生成命令详细信息的文本。
    """
    # 如果命令是启用的
    if name in config.command_enabled:
        info = data_manager.commands[name]
        yield F'命令 {name} 的详细信息：'
        yield from format_info(info)
        # 如果命令有子命令
        if children := info.get('children'):
            for child_name, child_info in children.items():
                child_info['prefix'] = '  '
                yield F'  +-- 子命令 {child_name}'
                yield from format_info(child_info)
        return None
    # 如果命令不存在或被禁用
    yield F'命令 {name} 不存在或已被禁用！'


# 定义格式化命令信息的函数
def format_info(info: dict):
    """
    格式化并返回命令或子命令的详细信息。

    参数:
    - info: 命令信息字典

    该函数是一个生成器，用于逐条生成命令信息的文本。
    """
    prefix = info.get('prefix', '')
    yield F'{prefix}  +-- 用法：{info["description"]}'
    yield F'{prefix}  +-- 语法：{info["usage"]}'
    # 如果命令有参数
    if parameters := info.get('parameters'):
        yield F'{prefix}  参数说明：'
        for parameter, usage in parameters.items():
            yield F'{prefix}    +-- {parameter} — {usage}'
