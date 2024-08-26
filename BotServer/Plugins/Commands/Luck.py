# 导入随机模块
import random
# 导入日期时间模块
from datetime import date
# 导入MD5哈希算法
from hashlib import md5

# 导入NoneBot框架的命令响应功能
from nonebot import on_command
# 导入OneBot v11协议的适配器
from nonebot.adapters.onebot.v11 import GroupMessageEvent
# 导入日志记录功能
from nonebot.log import logger

# 导入自定义的工具函数
from Scripts.Utils import Rules, turn_message

# 定义不好的事情列表
bad_things = ('造世吞（直接放飞', '修机器（一修就炸', '挖矿（只挖到原石', '造建筑（啥都没有', '钓鱼（全部是垃圾', '刷附魔（刷的垃圾')
# 定义好的事情列表
good_things = ('造世吞（完美运行', '修机器（一修就好', '挖矿（挖到十钻石', '造建筑（要啥都有', '钓鱼（钓到把神弓', '刷附魔（一发就中')

# 记录加载命令的调试日志
logger.debug('加载命令 Luck 完毕！')
# 创建命令处理器，用于处理'luck'命令
matcher = on_command('luck', force_whitespace=True, rule=Rules.command_rule)


# 处理群组消息的函数
@matcher.handle()
async def handle_group(event: GroupMessageEvent):
    """
    处理群组消息事件，返回人品分析结果。

    参数:
    - event: 群组消息事件对象

    该函数通过调用 luck_handler 函数处理事件，并结束命令处理。
    """
    message = turn_message(luck_handler(event))
    # 回复消息，@发送者
    await matcher.finish(message, at_sender=True)


# 处理人品分析的函数
def luck_handler(event: GroupMessageEvent):
    """
    分析用户的人品并生成相关建议。

    参数:
    - event: 群组消息事件对象

    生成包含人品分析和建议的消息。
    """
    # 生成基于日期、群组ID和用户ID的哈希种子
    seed_hash = md5(F'{date.today()} {event.group_id} {event.user_id}'.encode())
    # 设置随机数种子
    random.seed(seed := int(seed_hash.hexdigest(), 16))
    # 生成随机的人品值
    luck_point = random.randint(10, 100)
    # 根据人品值生成不同的提示信息
    tips = '啧……'
    if luck_point > 90:
        tips = '哇！'
    elif luck_point > 60:
        tips = '喵~'
    elif luck_point > 30:
        tips = '呜……'
    # 生成人品分析结果
    yield F'你今天的人品为 {luck_point}，{tips}'
    # 生成今日宜忌建议
    bad_thing = bad_things[(seed & event.group_id) % len(bad_things)]
    good_thing = good_things[(seed ^ event.group_id) % len(good_things)]
    yield F'今日宜：{good_thing}'
    if bad_thing.startswith(good_thing[:2]):
        bad_thing = bad_things[bad_things.index(bad_thing) - 1]
    yield F'今日忌：{bad_thing}'
