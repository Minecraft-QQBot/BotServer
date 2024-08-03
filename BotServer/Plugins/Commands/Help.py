from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message
from nonebot.log import logger
from nonebot.params import CommandArg

from Scripts.Config import config
from Scripts.Managers import data_manager
from Scripts.Utils import turn_message, rule

logger.debug('加载命令 Help 完毕！')
matcher = on_command('help', force_whitespace=True, rule=rule)


@matcher.handle()
async def handle_group(event: GroupMessageEvent, args: Message = CommandArg()):
    if name := args.extract_plain_text().strip():
        message = turn_message(detailed_handler(name))
        await matcher.finish(message)
    message = turn_message(help_handler())
    await matcher.finish(message)


def help_handler():
    yield '命令列表：'
    for name in config.command_enabled:
        info = data_manager.commands[name]
        yield F'  {name} — {data_manager.commands[name]["description"]}'
        if children := info.get('children'):
            for child_name, child_info in children.items():
                yield F'  +-- {name} {child_name} — {child_info["description"]}'
    yield '\n注：<name> 代表必填的参数，<*name> 代表此参数可选。对于所有需要输入 QQ 号的指令，可以通过 @ 此用户来代替输入的 QQ 号。'


def detailed_handler(name: str):
    if name in config.command_enabled:
        info = data_manager.commands[name]
        yield F'命令 {name} 的详细信息：'
        yield from format_info(info)
        if children := info.get('children'):
            for child_name, child_info in children.items():
                child_info['prefix'] = '  '
                yield F'  +-- 子命令 {child_name}'
                yield from format_info(child_info)
        return None
    yield F'命令 {name} 不存在或已被禁用！'


def format_info(info: dict):
    prefix = info.get('prefix', '')
    yield F'{prefix}  +-- 用法：{info["description"]}'
    yield F'{prefix}  +-- 语法：{info["usage"]}'
    if parameters := info.get('parameters'):
        yield F'{prefix}  参数说明：'
        for parameter, usage in parameters.items():
            yield F'{prefix}    +-- {parameter} — {usage}'
