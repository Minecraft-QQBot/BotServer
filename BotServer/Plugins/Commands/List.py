from Scripts.Managers import server_manager

from nonebot import get_plugin_config, on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message

from pydantic import BaseModel


class Config(BaseModel):
    bot_prefix: str = None
    command_groups: list = None
    command_enabled: list = None


config = get_plugin_config(Config)
matcher = on_command('list', force_whitespace=True)


@matcher.handle()
async def handle_group(event: GroupMessageEvent):
    if not (('list' in config.command_enabled) or (event.group_id in config.command_groups)):
        await matcher.finish()
    lines = tuple(list_handle())
    message = Message('\n'.join(lines))
    await matcher.finish(message)


def get_players():
    result = server_manager.execute('list')
    for name, value in result.items():
        players = value.strip().replace(' ', '')
        if len(players := players.split(':')) == 2:
            result[name] = players[1].split(',') if players[1] else []
            continue
        result[name] = []
    return result


def list_handle():
    player_count = 0
    if players := get_players:
        for name, value in players.items():
            yield F'====== {name} ======'
            if config.bot_prefix:
                fake_players, real_players = [], []
                for player in value:
                    player_count += 1
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
                continue
            player_count += len(value)
            yield ('    '.join(value) + '\n')
        yield F'当前在线人数共 {player_count} 人'
    else: yield '当前没有已连接的服务器！'
