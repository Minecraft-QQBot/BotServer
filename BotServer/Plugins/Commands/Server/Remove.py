from Scripts.Utils import rule
from Scripts.Config import config
from Scripts.Managers import server_manager, data_manager

from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message


matcher = on_command('server remove', force_whitespace=True, block=True, priority=5, rule=rule)


@matcher.handle()
async def handle_group(event: GroupMessageEvent, args: Message = CommandArg()):
    if str(event.user_id) not in config.superusers:
        await matcher.finish('你没有权限执行此命令！')
    if server := args.extract_plain_text().strip():
        message = server_remove_handler(server)
        await matcher.finish(message)
    await matcher.finish('请输入参数！')


def server_remove_handler(server: str):
    if name := server_manager.parse_server(server):
        data_manager.remove_server(name)
        server_manager.disconnect_server(name)
        data_manager.save()
        return F'已成功删除服务器 [{name}] ！'
    return F'未找到服务器 [{server}] ！请检查输入的内容是否为编号或名称。'

