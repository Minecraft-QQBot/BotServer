# from typing import Union
#
# from nonebot import on_command
# from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message
# from nonebot.log import logger
# from nonebot.params import CommandArg
#
# from Scripts.Config import config
# from Scripts.Managers import server_manager
# from Scripts.Utils import Rules, turn_message, get_permission, get_args
#
# logger.debug('加载命令 Set 完毕！')
# matcher = on_command('set', force_whitespace=True, rule=Rules.command_rule)
#
#
# @matcher.handle()
# async def handle_group(event: GroupMessageEvent, args: Message = CommandArg()):
#     if not get_permission(event):
#         await matcher.finish('您没有权限使用该命令！')
#     if args := get_args(args):
#         setattr(config, args[0], args[1])
#
#
# async def
