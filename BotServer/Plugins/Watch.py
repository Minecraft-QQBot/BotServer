from Scripts.Config import config
from Scripts.Managers import server_manager, data_manager

from nonebot import on_notice
from nonebot.adapters.onebot.v11 import GroupIncreaseNoticeEvent, GroupDecreaseNoticeEvent, MessageSegment, Message


matcher = on_notice()


@matcher.handle()
async def watch_decrease(event: GroupDecreaseNoticeEvent):
    if event.group_id not in config.command_groups:
        await matcher.finish()
    if player := data_manager.players.pop(str(event.user_id), None):
        server_manager.execute(F'whitelist remove {player}')
        await matcher.finish(F'用户 {event.user_id} 离开了群聊，自动从白名单中移除 {player} 玩家。')


@matcher.handle()
async def watch_increase(event: GroupIncreaseNoticeEvent):
    if event.group_id not in config.command_groups:
        await matcher.finish()
    at = MessageSegment.at(event.user_id)
    message = F'{at} 欢迎加入群聊！请仔细阅读群聊公告，并按照要求进行操作。'
    await matcher.finish(Message(message))

