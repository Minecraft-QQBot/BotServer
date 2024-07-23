from ..Utils import send_sync_message
from ..Config import config
from ..Managers import server_manager
from ..ServerWatcher import server_watcher

from json import dumps

from nonebot import get_driver
from nonebot.log import logger
from nonebot.drivers import HTTPServerSetup, ASGIMixin, Request, Response, URL


async def send_message(request: Request):
    if request.json.get('token') != config.token:
        return Response(403, content=dumps({'success': False}))
    if message := request.json.get('message'):
        logger.debug(F'发送消息到同步消息群！消息为 {message} 。')
        if await send_sync_message(message):
            return Response(200, content=dumps({'success': True}))
    logger.warning('发送消息失败！请检查机器人状态是否正确和群号是否填写正确。')
    return Response(500, content=dumps({'success': False}))


async def server_info(request: Request):
    if request.json.get('token') != config.token:
        return Response(403, content=dumps({'success': False}))
    pid = request.json.get('pid')
    name = request.json.get('name')
    server_watcher.append_server(name, pid)
    return Response(200, content=dumps({'success': True}))


async def server_startup(request: Request):
    if request.json.get('token') != config.token:
        return Response(403, content=dumps({'success': False}))
    logger.info('收到服务器开启数据！尝试连接到服务器……')
    pid = request.json.get('pid')
    name = request.json.get('name')
    server_watcher.append_server(name, pid)
    server_manager.connect_server(request.json)
    if config.broadcast_server:
        server_manager.broadcast(name, message='服务器已开启！', except_server=name)
        if await send_sync_message(F'服务器 [{name}] 已开启，喵～'):
            return Response(200, content=dumps({'success': True, 'flag': config.sync_all_game_message}))
        logger.warning('发送消息失败！请检查机器人状态是否正确和群号是否填写正确。')
        return Response(500, content=dumps({'success': False}))
    return Response(200, content=dumps({'success': True, 'flag': config.sync_all_game_message}))


async def server_shutdown(request: Request):
    if request.json.get('token') != config.token:
        return Response(403, content=dumps({'success': False}))
    logger.info('收到服务器关闭信息！正在断开连接……')
    name = request.json.get('name')
    server_manager.disconnect_server(name)
    server_watcher.remove_server(name)
    if config.broadcast_server:
        server_manager.broadcast(name, message='服务器已关闭！', except_server=name)
        if await send_sync_message(F'服务器 [{name}] 已关闭，呜……'):
            return Response(200, content=dumps({'success': True}))
        logger.warning('发送消息失败！请检查机器人状态是否正确和群号是否填写正确。')
        return Response(500, content=dumps({'success': False}))
    return Response(200, content=dumps({'success': True}))


async def player_info(request: Request):
    if request.json.get('token') != config.token:
        return Response(403, content=dumps({'success': False}))
    name = request.json.get('name')
    player = request.json.get('player')
    message = request.json.get('message')
    logger.debug(F'收到玩家 {player} 在服务器 [{name}] 发送消息！')
    if config.sync_all_game_message:
        if not (await send_sync_message(F'[{name}] <{player}> {message}')):
            logger.warning('发送消息失败！请检查机器人状态是否正确和群号是否填写正确。')
    if config.sync_message_between_servers:
        server_manager.broadcast(name, player, message, except_server=name)
    return Response(200, content=dumps({'success': True}))


async def player_joined(request: Request):
    if request.json.get('token') != config.token:
        return Response(403, content=dumps({'success': False}))
    logger.info('收到玩家加入服务器通知！')
    name = request.json.get('name')
    player = request.json.get('player')
    if config.broadcast_player:
        if config.bot_prefix and player.upper().startswith(config.bot_prefix):
            message = F'机器人 {player} 加入了 [{name}] 服务器。'
            server_manager.broadcast(name, message=F'机器人 {player} 加入了游戏。', except_server=name)
        else:
            message = F'玩家 {player} 加入了 [{name}] 服务器，喵～'
            server_manager.broadcast(name, message=F'玩家 {player} 加入了游戏，喵～', except_server=name)
        if await send_sync_message(message):
            return Response(200, content=dumps({'success': True}))
        logger.warning('发送消息失败！请检查机器人状态是否正确和群号是否填写正确。')
        return Response(500, content=dumps({'success': False}))
    return Response(200, content=dumps({'success': True}))
        


async def player_left(request: Request):
    if request.json.get('token') != config.token:
        return Response(403, content=dumps({'success': False}))
    logger.info('收到玩家离开服务器通知！')
    name = request.json.get('name')
    player = request.json.get('player')
    if config.broadcast_player:
        if config.bot_prefix and player.upper().startswith(config.bot_prefix):
            message = F'机器人 {player} 离开了 [{name}] 服务器。'
            server_manager.broadcast(name, message=F'机器人 {player} 离开了游戏。', except_server=name)
        else:
            message = F'玩家 {player} 离开了 [{name}] 服务器，呜……'
            server_manager.broadcast(name, message=F'玩家 {player} 离开了游戏，呜……', except_server=name)
        if await send_sync_message(message):
            return Response(200, content=dumps({'success': True}))
        logger.warning('发送消息失败！请检查机器人状态是否正确和群号是否填写正确。')
        return Response(500, content=dumps({'success': False}))
    return Response(200, content=dumps({'success': True}))


def setup_base_http_server():
    logger.info('正在载入基础 Http 服务器……')
    if isinstance(driver := get_driver(), ASGIMixin):
        http_server = HTTPServerSetup(URL('/send_message'), 'POST', 'send_message', send_message)
        driver.setup_http_server(http_server)
        http_server = HTTPServerSetup(URL('/player/info'), 'POST', 'player_info', player_info)
        driver.setup_http_server(http_server)
        http_server = HTTPServerSetup(URL('/player/left'), 'POST', 'player_left', player_left)
        driver.setup_http_server(http_server)
        http_server = HTTPServerSetup(URL('/player/joined'), 'POST', 'player_joined', player_joined)
        driver.setup_http_server(http_server)
        http_server = HTTPServerSetup(URL('/server/info'), 'POST','server_info', server_info)
        driver.setup_http_server(http_server)
        http_server = HTTPServerSetup(URL('/server/startup'), 'POST', 'server_startup', server_startup)
        driver.setup_http_server(http_server)
        http_server = HTTPServerSetup(URL('/server/shutdown'), 'POST', 'server_shutdown', server_shutdown)
        driver.setup_http_server(http_server)
        logger.success('基础 Http 服务器载入完毕！')
        return None
    logger.error('Http 服务器装载失败！请检查 Nonebot 驱动器后重试。')
    exit(1)
