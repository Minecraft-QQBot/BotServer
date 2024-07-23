from Scripts.Config import config
from Scripts.Managers import server_manager
from Scripts.Utils import turn_message, get_args, rule

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
    args = get_args(args)
    message = turn_message(command_handle(args))
    await matcher.finish(message)


def parse_command(command_args: list):
    command = ' '.join(command_args)
    if config.command_minecraft_whitelist:
        for enabled_command in config.command_minecraft_whitelist:
            if command.startswith(enabled_command):
                return command
        return None
    for disabled_command in config.command_minecraft_blacklist:
        if command.startswith(disabled_command):
            return None
    return command
    

def command_handle(args: list):
    if len(args) <= 1:
        yield '参数错误！请检查语法是否正确。'
        return None
    server_flag, * command = args
    if (command := parse_command(command)):
        server_flag = (None if server_flag == '*' else server_flag)
        if result := server_manager.execute(command, server_flag):
            if result:
                yield F'服务器 [{server_flag}] 执行命令完毕！返回值为 {result if result else "空"} 。'
                return None
            yield '命令已发送到所有服务器！服务器回应：'
            for name, response in result.items():
                yield F'  [{name}] -> {response if response else "无返回值"}'
            return None
        yield F'服务器 [{server_flag}] 不存在，请检查编号或名称是否输入正确。'
        return None
    yield '命令已被禁止！'

    