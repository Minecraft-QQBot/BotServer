# 导入必要的模块和函数
from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message
from nonebot.log import logger
from nonebot.params import CommandArg

# 导入自定义的模块和函数
from Scripts.Managers import server_manager, data_manager
from Scripts.Utils import Rules, get_player_name

# 初始化日志记录器并输出调试信息，表示'Send'命令已加载完成
logger.debug('加载命令 Send 完毕！')
# 定义一个命令匹配器，用于匹配并处理'send'命令，设置force_whitespace=True以强制预处理空格，rule参数指定命令规则
matcher = on_command('send', force_whitespace=True, rule=Rules.command_rule)


@matcher.handle()
async def handle_group(event: GroupMessageEvent, args: Message = CommandArg()):
    """
    处理群组消息命令。

    参数:
    - event: 群组消息事件对象，包含消息的上下文。
    - args: 用户发送的消息对象，通过CommandArg()参数获取。

    返回值:
    - 无返回值，但可能通过matcher.finish()结束命令处理。
    """
    # 提取并清理用户发送的纯文本消息内容
    if message := args.extract_plain_text().strip():
        # 尝试获取用户的玩家名称，如果无法获取则使用'未知用户'
        if name := data_manager.players.get(str(event.user_id), (get_player_name(event.sender.card), ))[0]:
            # 如果找到玩家名称，向服务器广播消息，并反馈给用户
            await server_manager.broadcast('QQ', name, message)
            await matcher.finish(F'已向服务器发送消息：{message}。')
        # 如果未找到玩家名称，以'未知用户'的名义向服务器广播消息，并提示用户未找到玩家名称
        await server_manager.broadcast('QQ', '未知用户', message)
        await matcher.finish(F'未找到你的玩家名称，请绑定后再试！已向服务器发送消息：{message}。')
    # 如果消息内容不符合预期，结束命令处理并提示用户参数错误
    await matcher.finish(F'参数错误，请检查命令格式！')
