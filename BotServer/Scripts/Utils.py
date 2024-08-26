# 导入所需的模块和库
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

# 导入NoneBot相关模块和自定义配置
from nonebot import get_bot
from nonebot.adapters.onebot.v11 import Event, Message, MessageEvent
from nonebot.exception import ActionFailed, NetworkError
from nonebot.log import logger

from .Config import config

# 编译正则表达式，用于提取玩家名称中的有效部分
regex = re.compile(R'[A-Z0-9_]+|\.[A-Z0-9_]+', re.IGNORECASE)


def turn_message(iterator: Iterable) -> Message:
    """
    将可迭代对象转换为Message对象。

    参数:
    - iterator: 一个可迭代对象，每项代表一条消息内容。

    返回:
    - 一个Message对象，包含迭代器中的所有内容，每项内容之间以换行符分隔。
    """
    lines = tuple(iterator)
    return Message('\n'.join(lines))


def get_player_name(name):
    """
    提取玩家名称中的有效部分。

    参数:
    - name: 玩家名称，可能包含无效字符。

    返回:
    - 提取的有效玩家名称，如果找不到有效部分则返回None。
    """
    if result := regex.search(name):
        return result.group()


def check_player(player: str):
    """
    检查玩家名称是否有效，并且长度是否符合要求。

    参数:
    - player: 玩家名称字符串。

    返回:
    - 布尔值，表示玩家名称是否有效。
    """
    if len(player) > 16:
        return False
    return get_player_name(player) == player


def get_args(args: Message):
    """
    从Message对象中提取参数。

    参数:
    - args: Message对象，可能包含文本和@消息段。

    返回:
    - 一个列表，包含提取出的所有参数。
    """
    result = []
    for segment in args:
        if segment.type == 'text':
            for arg in segment.data['text'].split(' '):
                arg and result.append(arg)
        elif segment.type == 'at':
            result.append(str(segment.data['qq']))
    logger.debug(f'从 {args} 中提取参数 {result} 完毕。')
    return result


def get_permission(event: MessageEvent):
    """
    判断事件发送者的权限是否满足条件。

    参数:
    - event: MessageEvent对象，包含事件相关信息。

    返回:
    - 布尔值，表示发送者是否具有足够权限。
    """
    return (str(event.user_id) in config.superusers) or (
            config.admin_superusers and event.sender.role in ('admin', 'owner')
    )


async def get_user_name(group: int, user: int):
    """
    异步获取群组中用户的昵称。

    参数:
    - group: 群组ID。
    - user: 用户ID。

    返回:
    - 用户的昵称或群名片，如果获取失败则返回None。
    """
    try:
        bot = get_bot()
        response = await bot.get_group_member_info(group_id=group, user_id=user)
    except (NetworkError, ActionFailed, ValueError):
        return None
    return response.get('card') or response.get('nickname')


async def send_synchronous_message(message: str):
    """
    异步发送消息到配置的群组。

    参数:
    - message: 要发送的消息内容。

    返回:
    - 布尔值，表示消息是否发送成功。
    """
    try:
        bot = get_bot()
        for group in config.message_groups:
            await bot.send_group_msg(group_id=group, message=message)
    except (NetworkError, ActionFailed, ValueError):
        return False
    return True


def restart():
    """
    重启应用，主要用于更新后重启。

    返回:
    - 布尔值，表示重启操作是否已经开始。
    """
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


class Json:
    @staticmethod
    def encode(data: dict):
        """
        将字典编码为Base64字符串。

        参数:
        - data: 要编码的字典。

        返回:
        - 编码后的Base64字符串。
        """
        string = dumps(data, ensure_ascii=False)
        string = b64encode(string.encode('Utf-8'))
        return string.decode('Utf-8')

    @staticmethod
    def decode(string: str):
        """
        将Base64字符串解码回字典。

        参数:
        - string: 要解码的Base64字符串。

        返回:
        - 解码后的字典，如果解码失败则返回None。
        """
        try:
            string = b64decode(string.encode('Utf-8'))
        except binascii.Error:
            logger.warning(f'无法解码字符串 {string}')
            return None
        return loads(string.decode('Utf-8'))


class Rules:
    @staticmethod
    def message_rule(event: Event):
        """
        判断事件是否满足消息转发的规则。

        参数:
        - event: Event对象，包含事件相关信息。

        返回:
        - 布尔值，表示事件是否满足转发规则。
        """
        if hasattr(event, 'group_id'):
            return event.group_id in config.message_groups
        return True

    @staticmethod
    def command_rule(event: Event):
        """
        判断事件是否满足命令执行的规则。

        参数:
        - event: Event对象，包含事件相关信息。

        返回:
        - 布尔值，表示事件是否满足命令执行规则。
        """
        if hasattr(event, 'group_id'):
            return event.group_id in config.command_groups
        return True
