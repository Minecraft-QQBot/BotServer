# 导入类型提示的Union模块
from typing import Union

# 导入NoneBot框架的相关模块，用于处理OneBot协议的群组消息事件
from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message
# 导入日志记录器
from nonebot.log import logger
# 导入参数解析器，用于解析命令参数
from nonebot.params import CommandArg

# 导入自定义配置管理模块
from Scripts.Config import config
# 导入服务器管理器，用于管理游戏服务器状态
from Scripts.Managers import server_manager
from Scripts.Utils import Rules, turn_message, get_permission, get_args


# 初始化命令处理相关的事件规则和匹配器
logger.debug('加载命令 Command 完毕！')
matcher = on_command('command', force_whitespace=True, rule=Rules.command_rule)


# 处理群组中的命令
@matcher.handle()
async def handle_group(event: GroupMessageEvent, args: Message = CommandArg()):
    # 检查用户权限，如果没有权限则结束命令处理
    if not get_permission(event):
        await matcher.finish('你没有权限执行此命令！')
    # 执行命令并处理结果
    flag, response = await execute_command(get_args(args))
    if flag is False:
        await matcher.finish(response)
    message = turn_message(command_handler(flag, response))
    await matcher.finish(message)


# 处理命令执行后的响应
def command_handler(name: str, response: Union[str, dict]):
    # 处理多服务器响应
    if isinstance(response, dict):
        yield '命令已发送到所有服务器！服务器回应：'
        for name, response in response.items():
            yield F'  [{name}] -> {response if response else "无返回值"}'
        return None
    # 处理单服务器响应
    yield F'命令已发送到服务器 [{name}]！服务器回应：{response if response else "无返回值"}'


# 解析和过滤命令
def parse_command(command: list):
    command = ' '.join(command)
    # 白名单模式：仅允许预设的命令
    if config.command_minecraft_whitelist:
        for enabled_command in config.command_minecraft_whitelist:
            if command.startswith(enabled_command):
                return command
        return None
    # 黑名单模式：禁止特定的命令
    for disabled_command in config.command_minecraft_blacklist:
        if command.startswith(disabled_command):
            return None
    return command


# 执行命令
async def execute_command(args: list):
    # 检查参数有效性
    if len(args) <= 1:
        return False, '参数不正确！请查看语法后再试。'
    server_flag, *command = args
    # 解析并过滤命令
    if command := parse_command(command):
        # 处理向所有服务器发送命令的情况
        if server_flag == '*':
            return True, await server_manager.execute(command)
        # 处理向特定服务器发送命令的情况
        if server := server_manager.get_server(server_flag):
            return server.name, await server.send_command(command)
        return False, F'服务器 [{server_flag}] 不存在！请检查插件配置。'
    return False, F'命令 {command} 已被禁止！'
