# 导入nonebot的命令处理器
from nonebot import on_command
# 导入OneBot v11的群组消息事件模型
from nonebot.adapters.onebot.v11 import GroupMessageEvent

# 导入数据管理器和一些实用工具
from Scripts.Managers import data_manager
from Scripts.Utils import Rules, turn_message, get_permission

# 定义一个命令处理器，用于处理'bound list'命令
matcher = on_command('bound list', force_whitespace=True, block=True, priority=5, rule=Rules.command_rule)


# 定义一个处理群组消息事件的异步函数
@matcher.handle()
async def handle_group(event: GroupMessageEvent):
    # 检查用户权限，如果没有权限则结束命令处理并提示用户
    if not get_permission(event):
        await matcher.finish('你没有权限执行此命令！')
    # 调用白名单列表处理器，转换消息并结束命令处理
    message = turn_message(bound_list_handler())
    await matcher.finish(message)


# 定义白名单列表处理器函数，该函数生成白名单列表的消息
def bound_list_handler():
    # 检查是否有玩家绑定数据
    if data_manager.players:
        yield '白名单列表：'
        for user, player in data_manager.players.items():
            yield F'  {user} -> {"、".join(player)}'
        return None
    # 如果没有绑定玩家，yield相应的提示消息
    yield '当前没有绑定任何玩家！'
