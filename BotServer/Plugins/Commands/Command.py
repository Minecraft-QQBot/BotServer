from typing import Union

from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message
from nonebot.log import logger
from nonebot.params import CommandArg

from Scripts.Config import config
from Scripts.Managers import server_manager
from Scripts.Utils import turn_message, get_permission, get_args, rule

logger.debug('命令 Command 加载完毕！')
matcher = on_command('command', force_whitespace=True, rule=rule)


@matcher.handle()
async def handle_group(event: GroupMessageEvent, args: Message = CommandArg()):
    if not get_permission(event):
        await matcher.finish('你没有权限执行此命令！')
    flag, response = await execute_command(get_args(args))
    if flag is False:
        await matcher.finish(response)
    message = turn_message(command_handler(flag, response))
    await matcher.finish(message)


def command_handler(name: str, response: Union[str, dict]):
    if isinstance(response, dict):
        yield '命令已发送到所有服务器！服务器回应：'
        for name, response in response.items():
            yield F'  [{name}] -> {response if response else "无返回值"}'
        return None
    yield F'命令已发送到服务器 [{name}]！服务器回应：{response if response else "无返回值"}'


def parse_command(command: list):
    command = ' '.join(command)
    if config.command_minecraft_whitelist:
        for enabled_command in config.command_minecraft_whitelist:
            if command.startswith(enabled_command):
                return command
        return None
    for disabled_command in config.command_minecraft_blacklist:
        if command.startswith(disabled_command):
            return None
    return command


async def execute_command(args: list):
    if len(args) <= 1:
        return False, '参数不正确！请查看语法后再试。'
    server_flag, *command = args
    if command := parse_command(command):
        if server_flag == '*':
            return True, await server_manager.execute(command)
        if server := server_manager.get_server(server_flag):
            return server.name, await server.send_command(command)
        return False, F'服务器 [{server_flag}] 不存在！请检查插件配置。'
    return False, F'命令 {command} 已被禁止！'
