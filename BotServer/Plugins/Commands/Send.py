from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message
from nonebot.log import logger
from nonebot.params import CommandArg

from Scripts.Managers import server_manager, data_manager
from Scripts.Utils import Rules, get_player_name

logger.debug('加载命令 Send 完毕！')
matcher = on_command('send', force_whitespace=True, rule=Rules.command_rule)


@matcher.handle()
async def handle_group(event: GroupMessageEvent, args: Message = CommandArg()):
    if message := args.extract_plain_text().strip():
        if name := data_manager.players.get(str(event.user_id), get_player_name(event.sender.card)):
            await server_manager.broadcast('QQ', name, message)
            await matcher.finish(F'已向服务器发送消息：{message}。')
        await server_manager.broadcast('QQ', '未知用户', message)
        await matcher.finish(F'未找到你的玩家名称，请绑定后再试！已向服务器发送消息：{message}。')
    await matcher.finish(F'参数错误，请检查命令格式！')
