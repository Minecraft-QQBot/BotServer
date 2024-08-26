# 导入必要的模块和函数
from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message
from nonebot.params import CommandArg

# 导入本地模块和函数
from Scripts.Config import config
from Scripts.Managers import data_manager, server_manager
from Scripts.Utils import Rules, get_user_name, get_permission, get_args
from .Base import async_lock

# 定义一个命令匹配器，用于处理"bound remove"命令
matcher = on_command('bound remove', force_whitespace=True, block=True, priority=5, rule=Rules.command_rule)


# 定义命令处理函数
@matcher.handle()
async def handle_group(event: GroupMessageEvent, args: Message = CommandArg()):
    # 解析命令参数
    if args := get_args(args):
        # 检查参数长度和类型
        if (len(args) == 1) and (not args[0].isdigit()):
            message = await bound_remove_handler(event, args)
            await matcher.finish(message)
        # 检查用户权限
        if not get_permission(event):
            await matcher.finish('你没有权限执行此命令！')
        message = await bound_remove_handler(event, args)
        await matcher.finish(message)
    # 默认处理情况
    message = await bound_remove_handler(event, [str(event.user_id)])
    await matcher.finish(message)


# 定义处理绑定移除逻辑的函数
async def bound_remove_handler(event: GroupMessageEvent, args: list):
    # 锁定以避免并发问题
    async with async_lock:
        # 检查参数数量和范围
        if not (0 <= len(args) <= 2):
            return '参数错误！请检查语法是否正确。'
        # 检查是否有已连接的服务器
        if not server_manager.check_online():
            return '当前没有有已连接的服务器，请稍后再次尝试！'
        # 处理只有一个参数的情况
        if len(args) == 1:
            if (unknown := args[0]).isdigit():
            # 如果参数是QQ号
                if user_name := await get_user_name(event.group_id, unknown):
                    if unknown not in data_manager.players:
                        return F'用户 {user_name}({unknown}) 还没有绑定白名单！请检查 QQ 号是否正确。'
                    bounded = data_manager.remove_player(unknown)
                    for player in bounded:
                        await server_manager.execute(F'{config.whitelist_command} remove {player}')
                    return F'已移除用户 {user_name}({unknown}) 绑定的所有白名单！'
            # 处理未知参数
            if data_manager.remove_player(str(event.user_id), unknown):
                await server_manager.execute(F'{config.whitelist_command} remove {unknown}')
                return F'已移除用户 {event.sender.card}({event.user_id}) 绑定的所有白名单！'
            return F'用户 {event.sender.card}({event.user_id}) 没有绑定名为 {unknown} 的白名单！'
        # 处理两个参数的情况
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
