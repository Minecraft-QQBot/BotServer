# 导入必要的库和模块
from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message
from nonebot.params import CommandArg

# 导入本地模块和配置
from Scripts.Config import config
from Scripts.Managers import server_manager, data_manager
from Scripts.Utils import Rules, get_permission, get_user_name, get_args, check_player
from .Base import async_lock

# 定义一个命令匹配器，用于处理 'bound append' 命令
matcher = on_command('bound append', force_whitespace=True, block=True, priority=5, rule=Rules.command_rule)


# 处理群组消息事件
@matcher.handle()
async def handle_group(event: GroupMessageEvent, args: Message = CommandArg()):
    # 检查用户权限，如果没有权限则结束命令执行
    if not get_permission(event):
        await matcher.finish('你没有权限执行此命令！')
    # 解析命令参数
    args = get_args(args)
    # 调用处理函数并等待结果
    message = await bound_append_handler(args, event.group_id)
    # 结束命令执行并返回结果
    await matcher.finish(message)


# 处理绑定添加逻辑的异步函数
async def bound_append_handler(args: list, group: int):
    # 上锁以确保线程安全
    async with async_lock:
        # 参数检查：参数数量不正确则返回错误信息
        if len(args) != 2: return '参数错误！请检查语法是否正确。'
        user, player = args
        # 参数检查：用户QQ号格式不正确则返回错误信息
        if not user.isdigit():
            return '参数错误！绑定的 QQ 号格式错误。'
        # 参数检查：玩家名称不合法则返回错误信息
        if not check_player(player):
            return '玩家名称非法！玩家名称只能包含字母、数字、下划线且长度不超过 16 个字符。'
        # 参数检查：如果玩家名称已绑定，则返回错误信息
        if data_manager.check_player_occupied(player):
            return '此玩家名称已经绑定过了，请换一个名称！'
        # 参数检查：如果没有连接的服务器，则返回错误信息
        if not server_manager.check_online():
            return '当前没有已链接的服务器，绑定失败！请连接后再试。'
        # 尝试获取用户昵称，如果用户不在群聊中则返回错误信息
        if user_name := await get_user_name(group, int(user)):
            # 尝试添加玩家绑定
            if data_manager.append_player(user, player):
                # 在服务器中添加玩家到白名单
                await server_manager.execute(F'{config.whitelist_command} add {player}')
                # 返回成功信息
                return F'用户 {user_name}({user}) 已绑定白名单到 {player} 玩家。'
            # 如果用户绑定的玩家数量过多则返回错误信息
            return '你绑定的玩家个数过多，绑定失败！'
        # 用户不在群聊中，返回错误信息
        return F'用户 {user} 不在此群聊！请检查 QQ 号是否正确。'
