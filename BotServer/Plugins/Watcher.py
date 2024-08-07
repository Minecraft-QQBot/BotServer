from datetime import datetime
from http import HTTPStatus

from httpx import AsyncClient
from nonebot import on_notice
from nonebot.adapters.onebot.v11 import (
    GroupDecreaseNoticeEvent,
    GroupIncreaseNoticeEvent,
    PokeNotifyEvent,
)
from nonebot.log import logger
from Scripts.Config import config
from Scripts.Managers import data_manager, server_manager
from Scripts.Utils import turn_message

matcher = on_notice()
week_mapping = ("一", "二", "三", "四", "五", "六", "日")


@matcher.handle()
async def watch_decrease(event: GroupDecreaseNoticeEvent) -> None:
    if event.group_id not in config.command_groups:
        return
    logger.info(f"检测到用户 {event.user_id} 离开了群聊！")
    if player := data_manager.remove_player(str(event.user_id)):
        await server_manager.execute(f"{config.whitelist_command} remove {player}")
        await matcher.finish(f'用户 {event.user_id} 离开了群聊，自动从白名单中移除 {"、".join(player)} 玩家。')


@matcher.handle()
async def watch_increase(event: GroupIncreaseNoticeEvent) -> None:
    if event.group_id not in config.command_groups:
        return
    await matcher.finish("欢迎加入群聊！请仔细阅读群聊公告，并按照要求进行操作。", at_sender=True)


@matcher.handle()
async def watch_poke(event: PokeNotifyEvent) -> None:
    if (event.group_id not in config.command_groups) and (not event.is_tome()):
        return
    message = turn_message(await poke_handler())
    await matcher.finish(message)


async def poke_handler() -> list[str]:
    ret = []
    now = datetime.now()
    ret.append(f'{now.strftime("%Y-%m-%d")} 星期{week_mapping[now.weekday()]}  {now.strftime("%H:%M:%S")}')
    async with AsyncClient() as client:
        response = await client.get("https://v1.jinrishici.com/all.json")
    if response.status_code == HTTPStatus.OK:
        data = response.json()
        ret.extend(
            (
                f'\n「 {data["content"]}」',
                f'               —— {data["author"]}《{data["origin"]}》',
            )
        )
    return ret
