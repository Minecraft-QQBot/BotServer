# 导入启动命令的装饰器
from nonebot import on_command
# 导入OneBot V11适配器中的群组消息事件和消息对象
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message
# 导入日志记录器
from nonebot.log import logger
# 导入获取命令参数的装饰器
from nonebot.params import CommandArg

# 导入全局范围的模板渲染函数
from Globals import render_template
# 导入配置管理器
from Scripts.Config import config
# 导入服务器管理器
from Scripts.Managers import server_manager
# 导入规则检查和消息转换的工具函数
from Scripts.Utils import Rules, turn_message
# 导入获取玩家UUID的网络请求函数
from Scripts.Network import get_player_uuid


# 初始化日志记录
logger.debug('加载命令 List 完毕！')
# 创建命令匹配器，用于匹配和处理 '/list' 命令
matcher = on_command('list', force_whitespace=True, rule=Rules.command_rule)


# 定义处理函数，用于处理群组消息事件和命令参数
@matcher.handle()
async def handle_group(event: GroupMessageEvent, args: Message = CommandArg()):
    # 提取命令参数中的服务器名称，如果没有提供则为 None
    server = (args.extract_plain_text().strip()) or None
    # 获取在线玩家信息
    flag, response = await get_players(server)
    # 如果获取失败，直接结束命令处理并返回错误信息
    if flag is False:
        await matcher.finish(response)
    # 如果配置了图片模式
    if config.image_mode:
        player_uuids = {}
        # 为每个在线玩家获取 UUID
        for players in response.values():
            for player in players[0]:
                player_uuids[player] = await get_player_uuid(player)
        # 渲染 HTML 模板生成玩家列表图片，并结束命令处理
        image = await render_template('List.html', (700, 1000), player_list=response, uuids=player_uuids)
        await matcher.finish(image)
    # 如果不使用图片模式，则将玩家列表转换为文本消息，并结束命令处理
    message = turn_message(list_handler(response))
    await matcher.finish(message)


# 定义函数，处理玩家列表信息
def list_handler(players: dict):
    # 如果只有一个服务器有玩家
    if len(players) == 1:
        server_name, players = players.popitem()
        online_count = sum(len(players) for players in players.values())
        # 返回服务器玩家列表的信息
        yield F'===== {server_name} 玩家列表 ====='
        yield from format_players(players)
        yield F'当前在线人数共 {online_count} 人'
        return None
    player_count = 0
    # 如果有多个服务器有玩家
    if players:
        yield '====== 玩家列表 ======'
        for name, value in players.items():
            if value is None:
                continue
            player_count += sum(len(players) for players in value)
            yield F' -------- {name} --------'
            yield from format_players(value)
        yield F'当前在线人数共 {player_count} 人'
        return None
    # 如果没有任何服务器连接
    yield '当前没有已连接的服务器！'


# 定义函数，格式化玩家和假人列表
def format_players(players: list):
    # 如果配置了假人前缀
    if config.bot_prefix:
        real_players, fake_players = players
        real_players_str = '\n    '.join(real_players)
        fake_players_str = '\n    '.join(fake_players)
        # 返回格式化的玩家和假人列表
        yield '  ———— 玩家 ————'
        if not real_players_str: real_players_str = '没有玩家在线！'
        yield '    ' + real_players_str
        yield '  ———— 假人 ————'
        if not fake_players_str: fake_players_str = '没有假人在线！'
        yield '    ' + fake_players_str + '\n'
        return None
    if players:
        yield '    ' + '\n    '.join(players) + '\n'
        return None
    yield '  没有玩家在线！\n'


# 定义函数，根据假人前缀分类玩家列表
def classify_players(players: list):
    if not config.bot_prefix:
        return players, []
    fake_players, real_players = [], []
    for player in players:
        if player.upper().startswith(config.bot_prefix):
            fake_players.append(player)
        else:
            real_players.append(player)
    return real_players, fake_players


# 异步函数，获取指定服务器或所有服务器的在线玩家信息
async def get_players(server_flag: str = None):
    # 如果没有指定服务器
    if server_flag is None:
        players = {
            name: classify_players(await server.send_player_list())
            for name, server in server_manager.servers.items() if server.status
        }
        return True, players
    # 如果指定了服务器，尝试查找并返回该服务器的在线玩家信息
    if server := server_manager.get_server(server_flag):
        return True, {server.name: classify_players(await server.send_player_list())}
    # 如果找不到指定的服务器
    return False, F'没有找到已连接的 [{server_flag}] 服务器！请检查编号或名称是否输入正确。'
