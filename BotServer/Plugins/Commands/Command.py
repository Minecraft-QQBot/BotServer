from Scripts.Config import config
from Scripts.Managers import server_manager
from Scripts.Utils import turn_message, get_args, rule

from typing import Union

from nonebot import on_command
from nonebot.log import logger
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message


logger.debug('命令 Command 加载完毕！')
matcher = on_command('command', force_whitespace=True, rule=rule)


@matcher.handle()
async def handle_group(event: GroupMessageEvent, args: Message = CommandArg()):
    if str(event.user_id) not in config.superusers:
        await matcher.finish('你没有权限执行此命令！')
    result = await parse_args(get_args(args))
    if isinstance(result, str):
        await matcher.finish(result)
    message = turn_message(format_response(* result))
    await matcher.finish(message)


async def parse_args(args: list):
    if len(args) <= 1:
        return '参数不正确！请查看语法后再试。'
    server_flag, * command = args
    command = ' '.join(server_flag)
    if config.command_minecraft_whitelist:
        for enabled_command in config.command_minecraft_whitelist:
            if command.startswith(enabled_command):
                return command
        return '命令已被服务器禁止。'
    for disabled_command in config.command_minecraft_blacklist:
        if command.startswith(disabled_command):
            return '命令已被服务器禁止。'
    server_flag = (None if server_flag == '*' else server_flag)
    if (response := await server_manager.execute(command, server_flag)) is not None:
        return server_flag, response
    return F'服务器 [{server_flag}] 不存在！请检查插件配置。'
    

def format_response(server_flag: str, response: Union[dict, str]):
    if isinstance(response, str):
        yield F'服务器 [{server_flag}] 执行命令完毕！返回值为 {response if response else "空"} 。'
        return None
    yield '命令已发送到所有服务器！服务器回应：'
    for name, response in response.items():
        yield F'  [{name}] -> {response if response else "无返回值"}'
    return None
    