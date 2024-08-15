from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message
from nonebot.params import CommandArg

from Scripts.Managers import data_manager
from Scripts.Utils import Rules, get_user_name, get_args

bound_query_matcher = on_command('bound query', force_whitespace=True, block=True, priority=5, rule=Rules.command_rule)


@bound_query_matcher.handle()
async def handle_group(event: GroupMessageEvent, args: Message = CommandArg()):
    if args := get_args(args):
        message = await bound_query_handler(args, event.group_id)
        await bound_query_matcher.finish(message)
    message = await bound_query_handler([str(event.user_id)], event.group_id)
    await bound_query_matcher.finish(message)


async def bound_query_handler(args: list, group: int):
    if len(args) != 1: return '参数错误！请检查语法是否正确。'
    if not (user := args[0]).isdigit():
        return '参数错误！绑定的 QQ 号格式错误。'
    if user_name := await get_user_name(group, int(user)):
        if user not in data_manager.players:
            return F'用户 {user_name}({user}) 还没有绑定白名单！'
        return F'用户 {user_name}({user}) 绑定的白名单有 {"、".join(data_manager.players[user])} 。'
    return F'用户 {user} 不在此群聊！请检查 QQ 号是否正确。'
