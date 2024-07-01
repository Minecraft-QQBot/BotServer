from Scripts.Utils import get_rule
from Scripts.Managers import server_manager, data_manager

from nonebot.params import CommandArg
from nonebot import get_plugin_config, on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message

from pydantic import BaseModel


class Config(BaseModel):
    superusers: list = None


config = get_plugin_config(Config)
matcher = on_command('server remove', force_whitespace=True, block=True, priority=5, rule=get_rule('server'))


@matcher.handle()
async def handle_group(event: GroupMessageEvent, args: Message = CommandArg()):
    if str(event.user_id) not in config.superusers:
        await matcher.finish('你没有权限执行此命令！')
    if server := args.extract_plain_text():
        message = server_remove_handle(server)
        await matcher.finish(message)
    await matcher.finish('请输入参数！')


def server_remove_handle(server: str):
    if name := server_manager.parse_server(server):
        data_manager.remove_server(name)
        server_manager.disconnect_server(name)
        return F'已成功删除服务器 [{name}] ！'
    return F'未找到服务器 [{server}] ！请检查输入的内容是否为编号或名称。'

