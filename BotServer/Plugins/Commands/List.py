from typing import Union

from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message
from nonebot.log import logger
from nonebot.params import CommandArg

from Scripts.Config import config
from Scripts.Managers import server_manager
from Scripts.Utils import Rules, turn_message

logger.debug('加载命令 List 完毕！')
matcher = on_command('list', force_whitespace=True, rule=Rules.command_rule)


@matcher.handle()
async def handle_group(event: GroupMessageEvent, args: Message = CommandArg()):
    server = (args.extract_plain_text().strip()) or None
    flag, response = await get_players(server)
    if flag is False:
        await matcher.finish(response)
    message = turn_message(list_handler(response, flag))
    await matcher.finish(message)


def list_handler(players: Union[dict, list], name: str = None):
    if isinstance(players, dict):
        player_count = 0
        if players:
            yield '====== 玩家列表 ======'
            for name, value in players.items():
                player_count += len(value)
                yield F' -------- {name} --------'
                yield from format_players(value)
            yield F'当前在线人数共 {player_count} 人'
            return None
        yield '当前没有已连接的服务器！'
        return None
    if players:
        yield F'===== [{name}] 玩家列表 ====='
        yield from format_players(players)
        yield F'当前在线人数共 {len(players)} 人'


def format_players(players: list):
    if config.bot_prefix:
        fake_players, real_players = [], []
        for player in players:
            if player.upper().startswith(config.bot_prefix.upper()):
                fake_players.append(player)
                continue
            real_players.append(player)
        real_players = '\n    '.join(real_players)
        fake_players = '\n    '.join(fake_players)
        yield '  ———— 玩家 ————'
        if not real_players:
            real_players = '没有玩家在线！'
        yield '    ' + real_players
        yield '  ———— 假人 ————'
        if not fake_players:
            fake_players = '没有假人在线！'
        yield '    ' + fake_players + '\n'
        return None
    if players:
        yield '    ' + '\n    '.join(players) + '\n'
        return None
    yield '  没有玩家在线！\n'


async def get_players(server_flag: str = None):
    if server_flag is None:
        players = {name: await server.send_player_list() for name, server in server_manager.servers.items() if
                   server.status}
        return True, players
    if server := server_manager.get_server(server_flag):
        return server.name, await server.send_player_list()
    return False, F'没有找到已连接的 [{server_flag}] 服务器！请检查编号或名称是否输入正确。'
