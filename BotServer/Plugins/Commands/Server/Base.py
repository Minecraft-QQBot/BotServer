# 导入nonebot的命令装饰器
from nonebot import on_command
# 导入OneBot v11适配器的MessageEvent类，用于处理消息事件
from nonebot.adapters.onebot.v11 import MessageEvent

# 导入脚本管理器和数据管理器模块
from Scripts.Managers import server_manager, data_manager
# 导入脚本工具模块中的规则处理和消息转换函数
from Scripts.Utils import Rules, turn_message

# 定义一个命令处理器，用于处理'server'命令，设置优先级和命令规则
matcher = on_command('server', force_whitespace=True, priority=10, rule=Rules.command_rule)


# 定义异步事件处理函数，用于处理群组命令
@matcher.handle()
async def handle_group(event: MessageEvent):
    """
    处理'server'命令事件。

    参数:
    - event: MessageEvent类型，表示消息事件对象。

    返回值:
    无，通过matcher.finish()结束命令处理。
    """
    # 转换服务器状态消息
    message = turn_message(server_handler())
    # 结束命令处理并发送消息
    await matcher.finish(message)


# 定义服务器状态处理器函数
def server_handler():
    """
    获取并处理服务器状态信息的生成器函数。

    参数:
    无

    返回值:
    通过yield返回每台服务器的状态信息字符串。
    """
    # 初始化状态变量
    status = None
    # 遍历服务器列表
    for index, name in enumerate(data_manager.servers):
        # 尝试从服务器管理器获取服务器对象
        if server := server_manager.servers.get(name):
            status = '在线' if server.status else '离线'
            yield F'({(index + 1):0>2}) [{name}] -> {status}'
            continue
        yield F'({(index + 1):0>2}) [{name}] -> 离线'
    # 如果没有找到任何在线服务器
    if status is None:
        yield '当前没有已连接的服务器！请检查是否正确安装了插件或重启服务器后再试。'
