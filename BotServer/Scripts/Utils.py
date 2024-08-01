import binascii
import os
import re
from base64 import b64encode, b64decode
from json import loads, dumps

from nonebot import get_bot
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message
from nonebot.exception import NetworkError, ActionFailed
from nonebot.log import logger

from .Config import config

regex = re.compile(R'[A-Z0-9_]+', re.IGNORECASE)


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


def encode(data: dict):
    # 编码
    string = dumps(data)
    string = string.encode('Utf-8')
    string = b64encode(string)
    return string.decode('Utf-8')


def decode(string: str):
    string = string.encode('Utf-8')
    try:
        string = b64decode(string)
    except binascii.Error:
        return None
    return loads(string.decode('Utf-8'))


def restart():
    if os.name == 'nt':
        os.system('start "python Bot.py"')
        exit()
    return False


async def get_user_name(group: int, user: int):
    bot = get_bot()
    try:
        response = await bot.get_group_member_info(group_id=group, user_id=user)
    except (NetworkError, ActionFailed):
        return None
    return response.get('card') or response.get('nickname')


async def send_synchronous_message(message: str):
    try:
        bot = get_bot()
    except ValueError:
        return False
    for group in config.message_groups:
        try:
            await bot.send_group_msg(group_id=group, message=message)
        except (NetworkError, ActionFailed):
            return False
    return True
