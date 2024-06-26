from Scripts.Managers import data_manager

from nonebot import get_plugin_config, on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message

from pydantic import BaseModel


class Config(BaseModel):
    enable: str = None
    command_enabled: list = None


config = get_plugin_config(Config)
matcher = on_command('help', force_whitespace=True)


@matcher.handle()
async def handle_group(event: GroupMessageEvent, args: Message = CommandArg()):
    if event.group_id not in config.command_group:
        await matcher.finish()
    if name := args.extract_plain_text():
        lines = tuple(detailed_help_handle(name))
        message = Message('\n'.join(lines))
        await matcher.finish(message)
    lines = tuple(help_handle())
    message = Message('\n'.join(lines))
    await matcher.finish(message)


def help_handle():
    yield '命令列表：'
    for name in config.command_enabled:
        usage = data_manager.commands[name]['usage']
        yield F'  {name} — {usage}'


def detailed_help_handle(name: str):
    if name in config.command_enabled:
        info = data_manager.commands[name]
        yield F'命令 {name} 的详细信息：'
        yield F'  用法：{info['usage']}'
        yield F'  语法：{info['command']}'
        yield F'  参数说明：'
        for paramter, usage in info['parameters'].items():
            yield F'    {paramter} — {usage}'
    else: yield F'命令 {name} 不存在或已被禁用！'
