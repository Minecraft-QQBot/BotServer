from Scripts.Utils import turn_message
from Scripts.Config import config
from Scripts.Managers import server_manager, data_manager

from nonebot import on_notice
from nonebot.adapters.onebot.v11 import GroupIncreaseNoticeEvent, GroupDecreaseNoticeEvent, PokeNotifyEvent

import requests
from datetime import datetime


matcher = on_notice()
week_mapping = ('一', '二', '三', '四', '五', '六', '日')


@matcher.handle()
async def watch_decrease(event: GroupDecreaseNoticeEvent):
    if event.group_id not in config.command_groups:
        return None
    if player := data_manager.players.pop(str(event.user_id), None):
        server_manager.execute(F'{config.whitelist_command} remove {player}')
        await matcher.finish(F'用户 {event.user_id} 离开了群聊，自动从白名单中移除 {player} 玩家。')


@matcher.handle()
async def watch_increase(event: GroupIncreaseNoticeEvent):
    if event.group_id not in config.command_groups:
        return None
    await matcher.finish('欢迎加入群聊！请仔细阅读群聊公告，并按照要求进行操作。', at_sender=True)


@matcher.handle()
async def watch_poke(event: PokeNotifyEvent):
    if (event.group_id not in config.command_groups) and (not event.is_tome()):
        return None
    message = turn_message(poke_handler())
    await matcher.finish(message)


def poke_handler():
    now = datetime.now()
    yield F'{now.strftime("%Y-%m-%d")} 星期{week_mapping[now.weekday()]}  {now.strftime("%H:%M:%S")}'
    response = requests.get('https://v1.jinrishici.com/all.json')
    if response.status_code == 200:
        data = response.json()
        yield F'\n「 {data["content"]}」'
        yield F'               —— {data["author"]}《{data["origin"]}》'
