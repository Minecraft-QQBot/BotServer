import binascii
import inspect
import os
import re
from base64 import b64decode, b64encode
from collections.abc import Iterable
from json import dumps, loads
from pathlib import Path
from threading import Timer
from uvicorn.server import Server

from nonebot import get_bot
from nonebot.adapters.onebot.v11 import Event, Message, MessageEvent
from nonebot.exception import ActionFailed, NetworkError
from nonebot.log import logger

from .Config import config

regex = re.compile(R'[A-Z0-9_]+|\.[A-Z0-9_]+', re.IGNORECASE)


def turn_message(iterator: Iterable) -> Message:
    lines = tuple(iterator)
    return Message('\n'.join(lines))


def check_player(player: str):
    if len(player) > 16:
        return False
    return get_player_name(player) == player


def check_message(message: str):
    # 返回是否含有违禁词
    return any(word in message for word in config.sync_sensitive_words)


def get_args(args: Message):
    result = []
    for segment in args:
        if segment.type == 'text':
            for arg in segment.data['text'].split(' '):
                arg and result.append(arg)
        elif segment.type == 'at':
            result.append(str(segment.data['qq']))
    logger.debug(f'从 {args} 中提取参数 {result} 完毕。')
    return result


def get_player_name(name):
    if result := regex.search(name):
        return result.group()


def get_permission(event: MessageEvent):
    return (str(event.user_id) in config.superusers) or (
            config.admin_superusers and event.sender.role in ('admin', 'owner')
    )


def restart():
    frames = inspect.getouterframes(inspect.currentframe())
    servers = (info.frame.f_locals.get('server') for info in frames[::-1])
    server = next(server for server in servers if isinstance(server, Server))

    def core():
        file = Path('Bot.py').absolute()
        os.system(f'start python {file}')
        server.should_exit = True

    if os.name == 'nt':
        timer = Timer(2, core)
        timer.start()
        return True
    return False


async def get_user_name(group: int, user: int):
    try:
        bot = get_bot()
        response = await bot.get_group_member_info(group_id=group, user_id=user)
    except (NetworkError, ActionFailed, ValueError):
        return None
    return response.get('card') or response.get('nickname')


async def send_synchronous_message(message: str):
    try:
        bot = get_bot()
        for group in config.message_groups:
            await bot.send_group_msg(group_id=group, message=message)
    except (NetworkError, ActionFailed, ValueError):
        return False
    return True


class Json:
    @staticmethod
    def encode(data: dict):
        # 编码
        string = dumps(data, ensure_ascii=False)
        string = b64encode(string.encode('Utf-8'))
        return string.decode('Utf-8')

    @staticmethod
    def decode(string: str):
        try:
            string = b64decode(string.encode('Utf-8'))
        except binascii.Error:
            logger.warning(f'无法解码字符串 {string}')
            return None
        return loads(string.decode('Utf-8'))


class Rules:
    @staticmethod
    def message_rule(event: Event):
        if hasattr(event, 'group_id'):
            return event.group_id in config.message_groups
        return True

    @staticmethod
    def command_rule(event: Event):
        if hasattr(event, 'group_id'):
            return event.group_id in config.command_groups
        return True
