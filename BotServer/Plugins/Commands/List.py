from typing import Union

from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message
from nonebot.log import logger
from nonebot.params import CommandArg

from Scripts.Config import config
from Scripts.Managers import server_manager
from Scripts.Utils import turn_message, rule

logger.debug('加载命令 List 完毕！')
matcher = on_command('list', force_whitespace=True, rule=rule)


@matcher.handle()
async def handle_group(event: GroupMessageEvent, args: Message = CommandArg()):
    server = args if (args := args.extract_plain_text().strip()) else None
    result = await get_players(server)
    if isinstance(result, dict):
        message = turn_message(list_handler(result))
        await matcher.finish(message)
    message = turn_message(list_handler(*result))
    await matcher.finish(message)


def list_handler(players: Union[dict, list], arg: str = None):
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
        yield F'===== [{arg}] 玩家列表 ====='
        yield from format_players(players)
        yield F'当前在线人数共 {len(players)} 人'
        return None
    yield F'没有找到已连接的 [{arg}] 服务器！请检查编号或名称是否输入正确。'


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
        yield '\n    '.join(players) + '\n'
        return None
    yield '  没有玩家在线！\n'


async def get_players(server: str = None):
    if not server:
        result = await server_manager.execute('list')
        for name, value in result.items():
            players = value.strip().replace(' ', '')
            if len(players := players.split(':')) == 2:
                result[name] = players[1].split(',') if players[1] else []
                continue
            result[name] = []
        return result
    if players := await server_manager.execute('list', server):
        players = players.strip().replace(' ', '')
        if len(players := players.split(':')) == 2:
            return (players[1].split(',') if players[1] else []), server
        return []
