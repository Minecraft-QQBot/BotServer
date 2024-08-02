from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageEvent, Message
from nonebot.params import CommandArg

from Scripts.Managers import server_manager, data_manager
from Scripts.Utils import get_permission, rule

matcher = on_command('server remove', force_whitespace=True, block=True, priority=5, rule=rule)


@matcher.handle()
async def handle_group(event: MessageEvent, args: Message = CommandArg()):
    if not get_permission(event):
        await matcher.finish('你没有权限执行此命令！')
    if server_flag := args.extract_plain_text().strip():
        if server := server_manager.get_server(server_flag):
            data_manager.remove_server(server.name)
            await server.disconnect()
            await matcher.finish(F'已成功删除服务器 [{server.name}] ！')
        await matcher.finish(F'未找到服务器 [{server}] ！请检查输入的内容是否为编号或名称。')
    await matcher.finish('请输入参数！')
