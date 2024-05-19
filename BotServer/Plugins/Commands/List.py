from Config import config
from Minecraft import server_manager

from nonebot import on_command
from nonebot.adapters.onebot.v11 import PrivateMessageEvent, GroupMessageEvent, Message

matcher = on_command('list', force_whitespace=True)


@matcher.handle()
async def handle_group(event: GroupMessageEvent):
    if event.group_id != config.main_group:
        await matcher.finish()
    lines = tuple(list_handle())
    message = Message('\n'.join(lines))
    await matcher.finish(message)


@matcher.handle()
async def handle_private(event: PrivateMessageEvent):
    lines = tuple(list_handle())
    message = Message('\n'.join(lines))
    await matcher.finish(message)


def list_handle():
    player_count = 0
    result = server_manager.execute('list')
    if result:
        for name, value in result.items():
            yield F'====== {name} ======'
            fake_players, real_players = [], []
            players = value.strip().replace(' ', '')
            if len(players := players.split(':')) == 2:
                players = players[1].split(',') if players[1] else []
            else:
                players = []
            for player in players:
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
        yield F'当前在线人数共 {player_count} 人'
    else: yield '当前没有已连接的服务器！'
