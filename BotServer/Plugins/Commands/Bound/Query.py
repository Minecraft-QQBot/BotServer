from Scripts.Config import config
from Scripts.Managers import data_manager
from Scripts.Utils import get_user_name, get_rule, get_args

from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message


matcher = on_command('bound query', force_whitespace=True, block=True, priority=5, rule=get_rule('bound'))


@matcher.handle()
async def handle_group(event: GroupMessageEvent, args: Message = CommandArg()):
    if str(event.user_id) not in config.superusers:
        await matcher.finish('你没有权限执行此命令！')
    if args := get_args(args):
        message = await bound_query_handler(args, event.group_id)
        await matcher.finish(message)
    message = await bound_query_handler([str(event.user_id)], event.group_id)
    await matcher.finish(message)


async def bound_query_handler(args: list, group: int):
    if len(args) != 1: return '参数错误！请检查语法是否正确。'
    if not (user := args[0]).isdigit():
        return '参数错误！绑定的 QQ 号格式错误。'
    if user_name := await get_user_name(group, int(user)):
        return F'用户 {user} 不在此群聊！请检查 QQ 号是否正确。'
    if user in data_manager.players:
        return F'用户 {user_name}({user}) 没有绑定白名单！'
    return F'用户 {user_name}({user}) 绑定的白名单为 {data_manager.players[user]}！'

    