from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message
from nonebot.log import logger
from nonebot.params import CommandArg

from Globals import render_template
from Scripts.Config import config
from Scripts.Managers import server_manager
from Scripts.Utils import Rules, turn_message
from Scripts.Network import get_player_uuid

logger.debug('加载命令 List 完毕！')
matcher = on_command('list', force_whitespace=True, rule=Rules.command_rule)


@matcher.handle()
async def handle_group(event: GroupMessageEvent, args: Message = CommandArg()):
    server = (args.extract_plain_text().strip()) or None
    flag, response = await get_players(server)
    if flag is False:
        await matcher.finish(response)
    if config.image_mode:
        player_uuids = {}
        for players in response.values():
            for player in players[0]:
                player_uuids[player] = await get_player_uuid(player)
        image = await render_template('List.html', (700, 1000), player_list=response, uuids=player_uuids)
        await matcher.finish(image)
    message = turn_message(list_handler(response))
    await matcher.finish(message)


def list_handler(players: dict):
    if len(players) == 1:
        server_name, players = players.popitem()
        yield F'===== {server_name} 玩家列表 ====='
        yield from format_players(players)
        # 计算在线人数
        online_count = sum(len(players) for players in players.values())
        yield F'当前在线人数共 {online_count} 人'
        return None
    player_count = 0
    if players:
        yield '====== 玩家列表 ======'
        for name, value in players.items():
            # 确保 value 是一个列表
            if isinstance(value, list):
                # 获取在线人数
                # 注意：value 是一个包含两个列表的列表，因此需要计算两个列表的长度之和
                count = len(value[0]) + len(value[1])
                player_count += count
                yield F' -------- {name} --------'
                yield from format_players(value)
            else:
                # 如果 value 不是列表，则忽略
                continue
        yield F'当前在线人数共 {player_count} 人'
        return None
    yield '当前没有已连接的服务器！'





def format_players(players: list):
    if config.bot_prefix:
        # 检查 players 是否足够长以进行解包
        if len(players) == 2:
            real_players, fake_players = players
        else:
            # 如果不够长，则直接使用 players 作为 real_players，并设置 fake_players 为空
            real_players, fake_players = players[0], []
        real_players_str = '\n    '.join(real_players)
        fake_players_str = '\n    '.join(fake_players)
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



def classify_players(players: list):
    if not config.bot_prefix:
        # 当 config.bot_prefix 为 False 时，返回一个包含两个列表的列表
        return [players, []]
    fake_players, real_players = [], []
    for player in players:
        if player.upper().startswith(config.bot_prefix):
            fake_players.append(player)
        else:
            real_players.append(player)
    return [real_players, fake_players]


async def get_players(server_flag: str = None):
    if server_flag is None:
        players = {
            name: classify_players(await server.send_player_list())
            for name, server in server_manager.servers.items() if server.status
        }
        return True, players
    if server := server_manager.get_server(server_flag):
        return True, {server.name: classify_players(await server.send_player_list())}
    return False, F'没有找到已连接的 [{server_flag}] 服务器！请检查编号或名称是否输入正确。'
