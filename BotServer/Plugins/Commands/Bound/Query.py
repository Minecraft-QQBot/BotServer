# 导入必要的模块
from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message
from nonebot.params import CommandArg

# 导入自定义的模块
from Scripts.Managers import data_manager
from Scripts.Utils import Rules, get_user_name, get_args

# 定义一个命令处理器，用于处理 'bound query' 命令
# 使用 whitespace 强制参数是为了确保命令能够正确解析
matcher = on_command('bound query', force_whitespace=True, block=True, priority=5, rule=Rules.command_rule)


# handle_group 函数用于处理群聊中的命令
# 参数 event 是群聊事件，args 是命令的参数
@matcher.handle()
async def handle_group(event: GroupMessageEvent, args: Message = CommandArg()):
    # 检查命令参数是否有效
    if args := get_args(args):
        # 调用 bound_query_handler 函数处理查询请求
        message = await bound_query_handler(args, event.group_id)
        # 发送查询结果并结束命令处理
        await matcher.finish(message)
    # 如果没有提供参数，则默认查询发送命令的用户
    message = await bound_query_handler([str(event.user_id)], event.group_id)
    # 发送查询结果并结束命令处理
    await matcher.finish(message)


# bound_query_handler 函数用于处理绑定查询请求
# 参数 args 是查询的参数，group 是群聊的 ID
async def bound_query_handler(args: list, group: int):
    # 检查参数数量是否正确
    if len(args) != 1: return '参数错误！请检查语法是否正确。'
    # 检查参数是否为数字
    if not (user := args[0]).isdigit():
        return '参数错误！绑定的 QQ 号格式错误。'
    # 获取用户昵称
    if user_name := await get_user_name(group, int(user)):
        # 检查用户是否已经绑定白名单
        if user not in data_manager.players:
            return F'用户 {user_name}({user}) 还没有绑定白名单！'
        # 返回用户的绑定信息
        return F'用户 {user_name}({user}) 绑定的白名单有 {"、".join(data_manager.players[user])} 。'
    # 如果用户不在群聊中，则返回错误信息
    return F'用户 {user} 不在此群聊！请检查 QQ 号是否正确。'
