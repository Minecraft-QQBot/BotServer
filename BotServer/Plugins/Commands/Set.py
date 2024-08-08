from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message
from nonebot.log import logger
from nonebot.params import CommandArg

from Scripts.Config import config
from Scripts.Utils import Rules, get_permission

allow_setting = ('sync_all_game_message', 'broadcast_player', 'broadcast_server')

logger.debug('加载命令 Set 完毕！')
matcher = on_command('set', force_whitespace=True, rule=Rules.command_rule)


@matcher.handle()
async def handle_group(event: GroupMessageEvent, args: Message = CommandArg()):
    if not get_permission(event):
        await matcher.finish('你没有权限执行此命令！')
    message = set_handler(args)
    await matcher.finish(message)


def set_handler(args: list):
    if len(args) == 1:
        key = args[0].lower()
        if key in allow_setting:
            return F'当前 {key} 的值为 {getattr(config, key)}！'
        return F'选项 {key} 不存在或者不支持该操作！'
    elif len(args) == 2:
        key, value = args
        key = key.lower()
        if key not in allow_setting:
            return F'选项 {key} 不存在或者不支持该操作！'
        value = bool(value)
        setattr(config, key, value)
        return F'已设置 {key} 为 {value}！'
    return '参数错误！请查看语法后再试。'
