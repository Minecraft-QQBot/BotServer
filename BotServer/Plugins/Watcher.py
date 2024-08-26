# 导入日期时间处理模块
from datetime import datetime

# 导入NoneBot2框架的相关模块和功能
from nonebot import on_notice
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import GroupDecreaseNoticeEvent, GroupIncreaseNoticeEvent, PokeNotifyEvent

# 导入自定义的模块和功能
from Scripts.Network import request
from Scripts.Config import config
from Scripts.Managers import data_manager, server_manager
from Scripts.Utils import Rules, turn_message

# 创建一个事件匹配器，用于处理通知类型的事件
matcher = on_notice(rule=Rules.message_rule, priority=15, block=False)
# 定义一个元组，用于映射星期几的数字到中文字符
week_mapping = ('一', '二', '三', '四', '五', '六', '日')


@matcher.handle()
async def watch_decrease(event: GroupDecreaseNoticeEvent):
    """
    监听群成员减少事件
    :param event: 群成员减少的通知事件
    """
    # 当有用户离开群聊时，记录日志信息
    logger.info(F'检测到用户 {event.user_id} 离开了群聊！')
    # 如果离开的用户是玩家，并且在数据管理器中找到了该用户的信息
    if player := data_manager.remove_player(str(event.user_id)):
        # 从服务器中移除该用户的白名单权限
        await server_manager.execute(F'{config.whitelist_command} remove {player}')
        # 发送消息，确认用户已从白名单中移除
        await matcher.finish(F'用户 {event.user_id} 离开了群聊，自动从白名单中移除 {"、".join(player)} 玩家。')


@matcher.handle()
async def watch_increase(event: GroupIncreaseNoticeEvent):
    """
    监听群成员增加事件
    :param event: 群成员增加的通知事件
    """
    # 当有新用户加入群聊时，发送欢迎消息并告知其阅读群公告
    await matcher.finish('欢迎加入群聊！请仔细阅读群聊公告，并按照要求进行操作。', at_sender=True)


@matcher.handle()
async def watch_poke(event: PokeNotifyEvent):
    """
    监听戳一戳事件
    :param event: 戳一戳通知事件
    """
    # 如果事件不是针对自己的戳一戳，则不进行任何操作
    if not event.is_tome():
        return None
    # 发起请求，获取一句随机的诗词
    sentence = await request('https://v1.jinrishici.com/all.json')
    # 将获取到的诗词信息转换为消息格式
    message = turn_message(poke_handler(sentence))
    # 发送消息，包含随机诗词信息
    await matcher.finish(message)


def poke_handler(sentence):
    """
    处理戳一戳事件的消息内容生成
    :param sentence: 获取到的诗词信息
    :yield: 生成器，产出处理后的消息内容
    """
    # 获取当前日期和时间
    now = datetime.now()
    # 生成并输出当前日期和时间的消息
    yield F'{now.strftime("%Y-%m-%d")} 星期{week_mapping[now.weekday()]}  {now.strftime("%H:%M:%S")}'
    # 如果获取到了有效的诗词信息
    if sentence is not None:
        # 生成并输出诗词内容和作者信息
        yield F'\n「{sentence["content"]}」'
        yield F'               —— {sentence["author"]}《{sentence["origin"]}》'
