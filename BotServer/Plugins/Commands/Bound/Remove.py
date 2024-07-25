from Scripts.Config import config
from Scripts.Utils import get_user_name, get_args, rule
from Scripts.Managers import data_manager, server_manager

import asyncio

from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message


async_look = asyncio.Lock()
matcher = on_command('bound remove', force_whitespace=True, block=True, priority=5, rule=rule)


@matcher.handle()
async def handle_group(event: GroupMessageEvent, args: Message = CommandArg()):
    if args := get_args(args):
        if (len(args) == 1) and (not args[0].isdigit()):
            message = await bound_remove_handler(event, args)
        if str(event.user_id) not in config.superusers:
            await matcher.finish('你没有权限执行此命令！')
        message = await bound_remove_handler(event, args)
        await matcher.finish(message)
    message = await bound_remove_handler(event, [str(event.user_id)])
    await matcher.finish(message)


async def bound_remove_handler(event: GroupMessageEvent, args: list):
    async with async_look:
        if not (0 <= len(args) <= 2):
            return '参数错误！请检查语法是否正确。'
        if not server_manager.check_online():
            return '当前没有有已连接的服务器，请稍后再次尝试！'
        if len(args) == 1:
            if (unknown := args[0]).isdigit():
                if user_name := await get_user_name(event.group_id, unknown):
                    if unknown not in data_manager.players:
                        return F'用户 {user_name}({unknown}) 还没有绑定白名单！请检查 QQ 号是否正确。'
                    bounded = data_manager.remove_player(unknown)
                    for player in bounded:
                        await server_manager.execute(F'{config.whitelist_command} remove {player}')
                    return F'已移除用户 {user_name}({unknown}) 绑定的所有白名单！'
            if data_manager.remove_player(str(event.user_id), unknown):
                await server_manager.execute(F'{config.whitelist_command} remove {unknown}')
                return F'已移除用户 {event.sender.card}({event.user_id}) 绑定的所有白名单！'
            return F'用户 {event.sender.card}({event.user_id}) 没有绑定名为 {unknown} 的白名单！'
        user, player = args
        if not user.isdigit():
            return '参数错误！删除绑定的 QQ 号格式错误。'
        if user_name := await get_user_name(event.group_id, user):
            if user not in data_manager.players:
                return F'用户 {user_name}({user}) 还没有绑定白名单！'
            if data_manager.remove_player(user, player):
                await server_manager.execute(F'{config.whitelist_command} remove {player}')
                return F'用户 {user} 已经从白名单中移除！'
            return F'用户 {user_name}({user}) 没有绑定名为 {player} 的白名单！'
