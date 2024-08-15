from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message
from nonebot.params import CommandArg

from Scripts.Config import config
from Scripts.Managers import server_manager, data_manager
from Scripts.Utils import Rules, get_permission, get_user_name, get_args, check_player
from .Base import async_lock

bound_append_matcher = on_command('bound append', force_whitespace=True, block=True, priority=5,
                                  rule=Rules.command_rule)


@bound_append_matcher.handle()
async def handle_group(event: GroupMessageEvent, args: Message = CommandArg()):
    if not get_permission(event):
        await bound_append_matcher.finish('你没有权限执行此命令！')
    args = get_args(args)
    message = await bound_append_handler(args, event.group_id)
    await bound_append_matcher.finish(message)


async def bound_append_handler(args: list, group: int):
    async with async_lock:
        if len(args) != 2: return '参数错误！请检查语法是否正确。'
        user, player = args
        if not user.isdigit():
            return '参数错误！绑定的 QQ 号格式错误。'
        if not check_player(player):
            return '玩家名称非法！玩家名称只能包含字母、数字、下划线且长度不超过 16 个字符。'
        if data_manager.check_player_occupied(player):
            return '此玩家名称已经绑定过了，请换一个名称！'
        if not server_manager.check_online():
            return '当前没有已链接的服务器，绑定失败！请连接后再试。'
        if user_name := await get_user_name(group, int(user)):
            if data_manager.append_player(user, player):
                await server_manager.execute(F'{config.whitelist_command} add {player}')
                return F'用户 {user_name}({user}) 已绑定白名单到 {player} 玩家。'
            return '你绑定的玩家个数过多，绑定失败！'
        return F'用户 {user} 不在此群聊！请检查 QQ 号是否正确。'
