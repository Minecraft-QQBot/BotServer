from datetime import datetime

from httpx import AsyncClient
from nonebot import on_notice
from nonebot.adapters.onebot.v11 import GroupDecreaseNoticeEvent, GroupIncreaseNoticeEvent, PokeNotifyEvent
from nonebot.log import logger

from Scripts.Config import config
from Scripts.Managers import data_manager, server_manager
from Scripts.Utils import Rules, turn_message

watch_matcher = on_notice(rule=Rules.message_rule)
week_mapping = ('一', '二', '三', '四', '五', '六', '日')


@watch_matcher.handle()
async def watch_decrease(event: GroupDecreaseNoticeEvent):
    logger.info(F'检测到用户 {event.user_id} 离开了群聊！')
    if player := data_manager.remove_player(str(event.user_id)):
        await server_manager.execute(F'{config.whitelist_command} remove {player}')
        await watch_matcher.finish(F'用户 {event.user_id} 离开了群聊，自动从白名单中移除 {"、".join(player)} 玩家。')


@watch_matcher.handle()
async def watch_increase(event: GroupIncreaseNoticeEvent):
    await watch_matcher.finish('欢迎加入群聊！请仔细阅读群聊公告，并按照要求进行操作。', at_sender=True)


@watch_matcher.handle()
async def watch_poke(event: PokeNotifyEvent):
    if not event.is_tome():
        return
    sentence = await get_sentence()
    message = turn_message(poke_handler(sentence))
    await watch_matcher.finish(message)


def poke_handler(sentence):
    now = datetime.now()
    yield F'{now.strftime("%Y-%m-%d")} 星期{week_mapping[now.weekday()]}  {now.strftime("%H:%M:%S")}'
    if sentence:
        yield F'\n「{sentence["content"]}」'
        yield F'               —— {sentence["author"]}《{sentence["origin"]}》'


async def get_sentence():
    async with AsyncClient() as client:
        response = await client.get('https://v1.jinrishici.com/all.json')
    if response.status_code == 200:
        return response.json()
