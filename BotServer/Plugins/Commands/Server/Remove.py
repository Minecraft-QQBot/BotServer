from Scripts.Utils import rule
from Scripts.Config import config
from Scripts.Managers import server_manager, data_manager

from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import MessageEvent, Message


matcher = on_command('server remove', force_whitespace=True, block=True, priority=5, rule=rule)


@matcher.handle()
async def handle_group(event: MessageEvent, args: Message = CommandArg()):
    if str(event.user_id) not in config.superusers:
        await matcher.finish('你没有权限执行此命令！')
    if server_flag := args.extract_plain_text().strip():
        if server := server_manager.get_server(server_flag):
            data_manager.remove_server(server.name)
            await server_manager.disconnect_server(server.name)
            await matcher.finish(F'已成功删除服务器 [{server.name}] ！')
        await matcher.finish(F'未找到服务器 [{server}] ！请检查输入的内容是否为编号或名称。')
    await matcher.finish('请输入参数！')
