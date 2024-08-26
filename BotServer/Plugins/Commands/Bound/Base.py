# 导入异步锁机制，用于控制并发访问
import asyncio

# 导入nonebot的命令处理器和事件适配器
from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message
from nonebot.params import CommandArg

# 导入配置和相关管理器模块
from Scripts.Config import config
from Scripts.Managers import data_manager, server_manager
from Scripts.Utils import Rules, check_player

# 创建一个异步锁，用于在处理绑定命令时防止并发问题
async_lock = asyncio.Lock()
# 注册一个命令处理器，用于处理'bound'命令
matcher = on_command('bound', force_whitespace=True, priority=10, rule=Rules.command_rule)


# 命令处理器的处理函数
@matcher.handle()
async def handle_group(event: GroupMessageEvent, args: Message = CommandArg()):
    # 尝试从命令参数中提取玩家名称
    if player := args.extract_plain_text().strip():
        # 如果提取成功，则调用绑定处理函数并结束命令处理
        message = await bound_handler(event, player)
        await matcher.finish(message)
    # 如果没有提供玩家名称，则提示用户
    await matcher.finish('请输入要绑定的玩家名称！')


# 处理玩家绑定逻辑的异步函数
async def bound_handler(event: GroupMessageEvent, player: str):
    # 使用异步锁确保绑定操作的线性执行
    async with async_lock:
        # 检查玩家名称是否合法
        if not check_player(player):
            return '此玩家名称非法！玩家名称应只包含字母、数字、下划线且长度不超过 16 个字符。'
        # 检查玩家是否已经绑定
        if player in data_manager.players:
            return '你已经绑定了白名单！请先解绑后尝试。'
        # 检查玩家名称是否已被其他用户绑定
        if data_manager.check_player_occupied(player):
            return '此玩家名称已经绑定过了，请换一个名称！'
        # 检查是否有已连接的服务器
        if not server_manager.check_online():
            return '当前没有已连接的服务器，绑定失败！请联系管理员连接后再试。'
        # 获取当前用户的QQ号码
        user = str(event.user_id)
        # 尝试将玩家与用户绑定
        if data_manager.append_player(user, player):
            # 在服务器中添加玩家到白名单
            await server_manager.execute(F'{config.whitelist_command} add {player}')
            # 返回绑定成功消息
            return F'用户 {event.sender.card}({user}) 已成功绑定白名单到 {player} 玩家。'
        # 如果绑定失败，可能是因为用户绑定的玩家数量过多
        return '你绑定的玩家个数过多，绑定失败！'
