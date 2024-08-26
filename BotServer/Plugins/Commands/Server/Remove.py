from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageEvent, Message
from nonebot.params import CommandArg

from Scripts.Managers import server_manager, data_manager
from Scripts.Utils import Rules, get_permission

# 声明处理命令'server remove'的匹配器，设置命令规则、是否阻塞、优先级等
matcher = on_command('server remove', force_whitespace=True, block=True, priority=5, rule=Rules.command_rule)


@matcher.handle()
async def handle_group(event: MessageEvent, args: Message = CommandArg()):
    """
    处理服务器移除命令的函数。

    参数:
    - event: 消息事件对象，用于获取事件相关信息。
    - args: 命令的参数，从消息中提取。

    函数首先检查用户是否有权限执行此命令，然后提取命令参数，尝试解析并移除对应的服务器。
    如果服务器存在，则从数据管理器中移除，并断开与服务器的连接，最后通知用户操作结果。
    """
    # 检查用户权限
    if not get_permission(event):
        await matcher.finish('你没有权限执行此命令！')
    # 提取并处理命令参数
    if server_flag := args.extract_plain_text().strip():
        if name := parse_flag(server_flag):
            data_manager.remove_server(name)
            if server := server_manager.servers.pop(name, None):
                await server.disconnect()
            await matcher.finish(F'已成功删除服务器 [{name}] ！')
        await matcher.finish(F'未找到服务器 [{server_flag}] ！请检查输入的内容是否为编号或名称。')
    await matcher.finish('请输入参数！')


def parse_flag(server_flag: str):
    """
    解析服务器标识符，支持数字编号或名称。

    参数:
    - server_flag: 服务器的标识符，可以是数字编号或名称。

    返回:
    - 如果输入是有效的数字编号，则返回对应的服务器名称；如果是名称且存在于数据管理器中，也返回名称。
    - 如果输入无效或找不到对应的服务器，返回None。
    """
    if server_flag.isdigit():
        server_flag = int(server_flag)
        if server_flag > len(data_manager.servers):
            return None
        return data_manager.servers[server_flag - 1]
    if server_flag in data_manager.servers:
        return server_flag
