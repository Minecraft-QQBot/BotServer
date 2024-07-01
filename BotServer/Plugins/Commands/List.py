from Scripts.Managers import server_manager
from Scripts.Utils import turn_message, get_rule

from nonebot.params import CommandArg
from nonebot import get_plugin_config, on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message

from pydantic import BaseModel


class Config(BaseModel):
    bot_prefix: str = None
    command_groups: list = None
    command_enabled: list = None


config = get_plugin_config(Config)
matcher = on_command('list', force_whitespace=True, rule=get_rule('list'))


@matcher.handle()
async def handle_group(event: GroupMessageEvent, args: Message = CommandArg()):
    server = args if (args := args.extract_plain_text()) else None
    message = turn_message(list_handler(server))
    await matcher.finish(message)


def get_players(server: str = None):
    if server is None:
        result = server_manager.execute('list')
        for name, value in result.items():
            players = value.strip().replace(' ', '')
            if len(players := players.split(':')) == 2:
                result[name] = players[1].split(',') if players[1] else []
                continue
            result[name] = []
        return result
    if players := server_manager.execute('list', server):
        players = players.strip().replace(' ', '')
        if len(players := players.split(':')) == 2:
            return players[1].split(',') if players[1] else []
        return []


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
        yield ('    ' + real_players)
        yield '  ———— 假人 ————'
        if not fake_players:
            fake_players = '没有假人在线！'
        yield ('    ' + fake_players + '\n')
        return None
    if players:
        yield ('  '.join(players) + '\n')
        return None
    yield '  没有玩家在线！\n'


def list_handler(server: str = None):
    if server is None:
        player_count = 0
        if players := get_players():
            yield '======= 玩家列表 ======='
            for name, value in players.items():
                player_count += len(value)
                yield F' ----- {name} -----'
                yield from format_players(value)
            yield F'当前在线人数共 {player_count} 人'
            return None
        yield '当前没有已连接的服务器！'
        return None
    if name := server_manager.parse_server(server):
        yield F'======= 服务器 {name} 玩家列表 ======='
        players = get_players(server)
        yield from format_players(players)
        yield F'当前在线人数共 {len(players)} 人'
        return None
    yield F'没有找到已连接的 [{server}] 服务器！请检查编号或名称是否输入正确。'
