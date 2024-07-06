from .Config import config

from nonebot.log import logger
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message

from string import ascii_letters, digits


letters = (ascii_letters + digits + '_')


def turn_message(iterator: iter):
    lines = tuple(iterator)
    return Message('\n'.join(lines))


def check_player(player: str):
    if len(player) > 16:
        return False
    for char in player:
        if char not in letters:
            return False
    return True


def get_args(args: Message):
    result = []
    for segment in args:
        if segment.type == 'text':
            for arg in segment.data['text'].split(' '):
                if arg: result.append(arg)
        elif segment.type == 'at':
            result.append(segment.data['qq'])
    logger.debug(F'提取参数 {result} 。')
    return result


def get_rule(name: str):
    def rule(event: GroupMessageEvent):
        nonlocal name
        return (name in config.command_enabled) and (event.group_id in config.command_groups)
    
    return rule
