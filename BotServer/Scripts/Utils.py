from .Config import config

from nonebot import get_bot
from nonebot.log import logger
from nonebot.exception import NetworkError, ActionFailed
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message, Bot

import binascii
from re import IGNORECASE, compile
from base64 import b64encode, b64decode

regex = compile(R'[A-Z0-9_]+', IGNORECASE)


def rule(event: GroupMessageEvent):
    return event.group_id in config.command_groups


def turn_message(iterator: iter):
    lines = tuple(iterator)
    return Message('\n'.join(lines))


def get_player_name(name):
    if result := regex.search(name):
        return result.group()


def check_player(player: str):
    if len(player) > 16:
        return False
    return get_player_name(player) == player


def get_args(args: Message):
    result = []
    for segment in args:
        if segment.type == 'text':
            for arg in segment.data['text'].split(' '):
                if arg: result.append(arg)
        elif segment.type == 'at':
            result.append(str(segment.data['qq']))
    logger.debug(F'从 {args} 中提取参数 {result} 完毕。')
    return result


def decode(string: str):
    string = string.encode('Utf-8')
    string = b64decode(string)
    return string.decode('Utf-8')


def encode(string: str):
    string = string.encode('Utf-8')
    try: string = b64encode(string)
    except binascii.Error: return None
    return string.decode('Utf-8')


async def get_user_name(group: int, user: int):
    bot = get_bot()
    try:
        response = await bot.get_group_member_info(group_id=group, user_id=user)
    except (NetworkError, ActionFailed):
        return None
    return response.get('card')


async def send_synchronous_message(message: str):
    try: bot = get_bot()
    except ValueError: return False
    for group in config.message_groups:
        try:
            await bot.send_group_msg(group_id=group, message=message)
        except (NetworkError, ActionFailed):
            return False
    return True
