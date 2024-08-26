# 导入nonebot的on_message装饰器，用于创建一个消息匹配器
from nonebot import on_message
# 导入OneBot v11适配器的GroupMessageEvent类，用于处理群组消息事件
from nonebot.adapters.onebot.v11 import GroupMessageEvent
# 导入nonebot的日志记录器
from nonebot.log import logger

# 导入配置管理器，用于访问配置信息
from Scripts.Config import config
# 导入服务器管理器和数据管理器，用于处理消息的转发和玩家数据的管理
from Scripts.Managers import server_manager, data_manager
# 导入工具函数，包括消息规则检查、获取玩家名和用户名
from Scripts.Utils import Rules, get_player_name, get_user_name

# 定义一个消息匹配器，用于处理符合特定规则的消息
matcher = on_message(rule=Rules.message_rule, priority=15, block=False)
# 映射消息中的不同类型到描述性字符串
mapping = {'record': '语音', 'image': '图片', 'reply': '回复', 'face': '表情', 'file': '文件'}


# 处理匹配到的消息，将群组消息转发到游戏内
@matcher.handle()
async def sync_message(event: GroupMessageEvent):
    # 如果配置为同步所有群消息
    if config.sync_all_qq_message:
        # 获取纯文本消息内容
        plain_text = event.get_plaintext()
        # 检查消息是否以命令前缀开始，如果是则不处理
        for start in config.command_start:
            if plain_text.startswith(start):
                return None
        # 将消息内容转换为适合转发的形式
        plain_text = await turn_text(event)
        # 获取发送消息的玩家名称
        name = data_manager.players.get(str(event.user_id), (get_player_name(event.sender.card), ))[0]
        # 广播消息到游戏内
        await server_manager.broadcast('QQ', (name or event.sender.nickname), plain_text)
        # 记录日志
        logger.debug(F'转发主群用户 {event.sender.card} 消息 {plain_text} 到游戏内。')


# 将消息内容转换为适合在游戏内展示的形式
async def turn_text(event: GroupMessageEvent):
    plain_texts = []
    for segment in event.get_message():
        # 处理文本类型的消息段
        if segment.type == 'text' and (text := segment.data['text']):
            plain_texts.append(text)
            continue
        # 处理@消息段，转换为对应玩家的名称
        if segment.type == 'at':
            user = str(segment.data['qq'])
            if player := data_manager.players.get(user):
                plain_texts.append(F'[@{player[0]}]')
                continue
            if player := get_player_name(await get_user_name(event.group_id, user)):
                plain_texts.append(F'[@{player}]')
                continue
            plain_texts.append(F'[@未知用户]')
            continue
        # 处理其他类型的消息段，如语音、图片等
        plain_texts.append(F'[{mapping.get(segment.type, "未知类型")}]')
    # 返回转换后的消息文本
    return ' '.join(plain_texts)
