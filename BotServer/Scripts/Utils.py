from nonebot import get_plugin_config
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message, Bot

from pydantic import BaseModel


class Config(BaseModel):
    command_groups: list = None
    command_enabled: list = None


config: Config = None


def turn_message(iterator: iter):
    lines = tuple(iterator)
    return Message('\n'.join(lines))    


def get_args(args: Message):
    result = []
    for segment in args:
        if segment.type == 'text':
            if text := segment.data['text']:
                for arg in text.split(' '):
                    result.append(arg)
        elif segment.type == 'at':
            result.append(segment.data['qq'])
    return result


def get_rule(name: str):
    def rule(event: GroupMessageEvent):
        nonlocal name
        return (name in config.command_enabled) and (event.group_id in config.command_groups)

    global config
    if not config:
        config = get_plugin_config(Config)
    return rule
