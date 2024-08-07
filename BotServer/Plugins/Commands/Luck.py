import random
from datetime import date
from hashlib import md5

from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.log import logger

from Scripts.Utils import Rules, turn_message

bad_things = ('造世吞（直接放飞', '修机器（一修就炸', '挖矿（只挖到原石')
good_things = ('造世吞（完美运行', '修机器（一修就好', '挖矿（挖到十钻石')

logger.debug('加载命令 Luck 完毕！')
matcher = on_command('luck', force_whitespace=True, rule=Rules.command_rule)


@matcher.handle()
async def handle_group(event: GroupMessageEvent):
    message = turn_message(luck_handler(event))
    await matcher.finish(message, at_sender=True)


def luck_handler(event: GroupMessageEvent):
    seed_hash = md5(F'{date.today()} {event.group_id} {event.user_id}'.encode())
    random.seed(seed := int(seed_hash.hexdigest(), 16))
    tips = '啧……'
    luck_point = random.randint(10, 100)
    if luck_point > 90:
        tips = '哇！'
    elif luck_point > 60:
        tips = '喵~'
    elif luck_point > 30:
        tips = '呜……'
    yield F'你今天的人品为 {luck_point}，{tips}'
    bad_thing = bad_things[(seed & event.group_id) % len(bad_things)]
    good_thing = good_things[(seed ^ event.group_id) % len(good_things)]
    yield F'今日宜：{good_thing}'
    if bad_thing.startswith(good_thing[:2]):
        bad_thing = bad_things[bad_things.index(bad_thing) - 1]
    yield F'今日忌：{bad_thing}'
