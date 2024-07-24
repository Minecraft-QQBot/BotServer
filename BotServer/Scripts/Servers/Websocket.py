from ..Config import config
from ..Managers import server_manager
from ..ServerWatcher import server_watcher
from ..Utils import send_sync_message

from json import dumps, loads

from nonebot import get_driver
from nonebot.log import logger
from nonebot.exception import WebSocketClosed
from nonebot.drivers import WebSocketServerSetup, WebSocket, ASGIMixin, URL


async def verify(websocket: WebSocket):
    logger.info('检测到 WebSocket 链接，正在验证身份……')
    data = loads(await websocket.receive())
    if data.get('token') != config.token and data.get('name'):
        await websocket.close()
        logger.warning('身份验证失败！请检查插件配置文件是否正确。')
        return None
    await websocket.send(dumps({'success': True}))
    logger.success(F'身份验证成功，服务器 [{(name := data["name"])}] 已连接到！WebSocket 连接已建立。')
    return name

async def handle_websocket_minecraft(websocket: WebSocket):
    await websocket.accept()
    if name := await verify(websocket):
        server_manager.append_server()
        

async def handle_websocket_bot(websocket: WebSocket):
    await websocket.accept()
    if name := await verify(websocket):
        try:
            while True:
                response = None
                message = loads(await websocket.receive())
                logger.debug(F'收到来数据 {message} 。')
                data = message.get('data')
                action = message.get('action')
                if action == 'send_message':
                    response = await send_message(name, data)
                elif action == 'server_info':
                    response = await server_info(name, data)
                elif action == 'server_startup':
                    response = await server_startup(name, data)
                elif action == 'server_shutdown':
                    response = await server_shutdown(name, data)
                elif action == 'player_info':
                    response = await player_info(name, data)
                elif action == 'player_joined':
                    response = await player_joined(name, data)
                elif action == 'player_left':
                    response = await player_left(name, data)
                if response is not None:
                    await websocket.send(dumps(response))
        except (ConnectionError, WebSocketClosed):
            logger.info('WebSocket 连接已关闭！')


async def send_message(name: str, data: dict):
    if message := data.get('message'):
        logger.debug(F'发送消息 {message} 到消息群！')
        if await send_sync_message(message):
            return {'success': True}
    logger.warning('发送消息失败！请检查机器人状态是否正确和群号是否填写正确。')
    return {'success': False}


async def server_info(name: str, data: dict):
    pid = data.get('pid')
    server_watcher.append_server(name, pid)
    await {'success': True}


async def server_startup(name: str, data: dict):
    logger.info('收到服务器开启数据！尝试连接到服务器……')
    pid = data.get('pid')
    server_manager.connect_server(data)
    server_watcher.append_server(name, pid)
    if config.broadcast_server:
        server_manager.broadcast(name, message='服务器已开启！', except_server=name)
        if await send_sync_message(F'服务器 [{name}] 已开启，喵～'):
            return {'success': True}
        logger.warning('发送消息失败！请检查机器人状态是否正确和群号是否填写正确。')
        await {'success': False}
    await {'success': True, 'flag': config.sync_all_game_message}


async def server_shutdown(name: str, data: dict):
    logger.info('收到服务器关闭信息！正在断开连接……')
    name = data.get('name')
    server_watcher.remove_server(name)
    server_manager.disconnect_server(name)
    if config.broadcast_server:
        server_manager.broadcast(name, message='服务器已关闭！', except_server=name)
        if await send_sync_message(F'服务器 [{name}] 已关闭，呜……'):
            return {'success': True}
        logger.warning('发送消息失败！请检查机器人状态是否正确和群号是否填写正确。')
        return {'success': False}
    await {'success': True}


async def player_info(name: str, data: dict):
    name = data.get('name')
    player = data.get('player')
    message = data.get('message')
    logger.debug(F'收到玩家 {player} 在服务器 [{name}] 发送消息！')
    if config.sync_all_game_message:
        if not (await send_sync_message(F'[{name}] <{player}> {message}')):
            logger.warning('发送消息失败！请检查机器人状态是否正确和群号是否填写正确。')
    if config.sync_message_between_servers:
        server_manager.broadcast(name, player, message, except_server=name)
    return {'success': True}


async def player_joined(name: str, data: dict):
    logger.info('收到玩家加入服务器通知！')
    player = data.get('player')
    if config.broadcast_player:
        server_message = F'玩家 {player} 加入了游戏。'
        message = F'玩家 {player} 加入了 [{name}] 服务器，喵～'
        if config.bot_prefix and player.upper().startswith(config.bot_prefix):
            message = F'机器人 {player} 加入了 [{name}] 服务器。'
            if config.sync_message_between_servers:
                server_message = F'机器人 {player} 加入了游戏。'
        if config.sync_message_between_servers:
            server_manager.broadcast(name, message=server_message, except_server=name)
        if await send_sync_message(message):
            return {'success': True}
        logger.warning('发送消息失败！请检查机器人状态是否正确和群号是否填写正确。')
        return {'success': False}
    return {'success': True}


async def player_left(name: str, message: dict):
    logger.info('收到玩家离开服务器通知！')
    player = message.get('player')
    if config.broadcast_player:
        server_message = F'玩家 {player} 离开了游戏。'
        message = F'玩家 {player} 离开了 [{name}] 服务器，呜……'
        if config.bot_prefix and player.upper().startswith(config.bot_prefix):
            server_message = F'机器人 {player} 离开了游戏。'
            message = F'机器人 {player} 离开了 [{name}] 服务器。'
        if config.sync_message_between_servers:
            server_manager.broadcast(name, message=server_message, except_server=name)
        if await send_sync_message(message):
            return {'success': True}
        logger.warning('发送消息失败！请检查机器人状态是否正确和群号是否填写正确。')
        return {'success': False}
    return {'success': True}


def setup_websocket_server():
    if isinstance((driver := get_driver()), ASGIMixin):
        driver.setup_websocket_server(WebSocketServerSetup(URL('/websokcet/bot'), 'bot', handle_websocket_bot))
        logger.success('装载 WebSocket 服务器成功！')
        return None
    logger.error('装载 WebSocket 服务器失败！请检查驱动是否正确。')
    exit(1)
