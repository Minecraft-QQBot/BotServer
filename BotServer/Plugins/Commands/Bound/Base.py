from Scripts.Config import config
from Scripts.Utils import check_player, rule
from Scripts.Managers import data_manager, server_manager

import asyncio

from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message


async_lock = asyncio.Lock()
matcher = on_command('bound', force_whitespace=True, priority=10, rule=rule)


@matcher.handle()
async def handle_group(event: GroupMessageEvent, args: Message = CommandArg()):
    if player := args.extract_plain_text().strip():
        message = await bound_handler(event, player)
        await matcher.finish(message)
    await matcher.finish('请输入要绑定的玩家名称！')


async def bound_handler(event: GroupMessageEvent, player: str):
    async with async_lock:
        if not check_player(player):
            return '此玩家名称非法！玩家名称应只包含字母、数字、下划线且长度不超过 16 个字符。'
        if player in data_manager.players:
            return '你已经绑定了白名单！请先解绑后尝试。'
        if data_manager.check_player_occupied(player):
            return '此玩家名称已经绑定过了，请换一个名称！'
        if not server_manager.check_online():
            return '当前没有已连接的服务器，绑定失败！请联系管理员连接后再试。'
        user = str(event.user_id)
        if data_manager.append_player(user, player):
            await server_manager.execute(F'{config.whitelist_command} add {player}')
            return F'用户 {event.sender.card}({user}) 已成功绑定白名单到 {player} 玩家。'
        return '你绑定的玩家个数过多，绑定失败！'