import asyncio

from nonebot import get_driver
from nonebot.drivers import WebSocketServerSetup, WebSocket, ASGIMixin, URL
from nonebot.exception import WebSocketClosed
from nonebot.log import logger

from ..Config import config
from ..Managers import server_manager, data_manager
from ..Utils import send_synchronous_message, decode, encode


async def verify(websocket: WebSocket):
    logger.info('检测到 WebSocket 链接，正在验证身份……')
    if info := websocket.request.headers.get('info'):
        info = decode(info)
        name = info.get('name')
        if info.get('token') != config.token or (not name):
            await websocket.close()
            logger.warning('身份验证失败！请检查插件配置文件是否正确。')
            return None
        logger.success(F'身份验证成功，服务器 [{name}] 已连接到！连接已建立。')
        return name


async def handle_websocket_minecraft(websocket: WebSocket):
    await websocket.accept()
    if name := await verify(websocket):
        data_manager.append_server(name)
        server_manager.append_server(name, websocket)
        await websocket.receive()
        while not websocket.closed:
            await asyncio.sleep(30)
        logger.info(F'检测到连接与 [{name}] 已断开！')


async def handle_websocket_bot(websocket: WebSocket):
    await websocket.accept()
    if name := await verify(websocket):
        try:
            while True:
                response = None
                receive_message = decode(await websocket.receive())
                if receive_message is None:
                    continue
                data = receive_message.get('data')
                event_type = receive_message.get('type')
                if event_type == 'message':
                    response = await message(name, data)
                elif event_type == 'server_startup':
                    response = await server_startup(name, data)
                elif event_type == 'server_shutdown':
                    response = await server_shutdown(name, data)
                elif event_type == 'player_chat':
                    response = await player_chat(name, data)
                elif event_type == 'player_death':
                    response = await player_death(name, data)
                elif event_type == 'player_left':
                    response = await player_left(name, data)
                elif event_type == 'player_joined':
                    response = await player_joined(name, data)
                if response is not None:
                    logger.debug(F'对来自 [{name}] 的数据 {receive_message}')
                    if response is True:
                        await websocket.send(encode({'success': True}))
                        continue
                    await websocket.send(encode({'success': True, 'data': response}))
                    continue
                logger.warning(F'收到来自 [{name}] 无法解析的数据 {receive_message}')
                await websocket.send(encode({'success': False}))
        except (ConnectionError, WebSocketClosed):
            logger.info('WebSocket 连接已关闭！')


async def message(name: str, group_message: str):
    if group_message:
        logger.debug(F'发送消息 {group_message} 到消息群！')
        return await send_synchronous_message(group_message) or None
    logger.warning('发送消息失败！请检查机器人状态是否正确和群号是否填写正确。')
    return True


async def server_startup(name: str, data: dict):
    logger.info('收到服务器开启数据！尝试连接到服务器……')
    data_manager.append_server(name)
    if config.broadcast_server:
        await server_manager.broadcast(name, message='服务器已开启！', except_server=name)
        if await send_synchronous_message(F'服务器 [{name}] 已开启，喵～'):
            return config.sync_all_game_message
        logger.warning('发送消息失败！请检查机器人状态是否正确和群号是否填写正确。')
        return None
    return config.sync_all_game_message


async def server_shutdown(name: str, data: dict):
    logger.info('收到服务器关闭信息！正在断开连接……')
    await server_manager.disconnect_server(name)
    if config.broadcast_server:
        await server_manager.broadcast(name, message='服务器已关闭！', except_server=name)
        if await send_synchronous_message(F'服务器 [{name}] 已关闭，呜……'):
            return True
        logger.warning('发送消息失败！请检查机器人状态是否正确和群号是否填写正确。')
        return None
    return True


async def player_chat(name: str, data: list):
    player, chat_message = data
    logger.debug(F'收到玩家 {player} 在服务器 [{name}] 发送消息！')
    if config.sync_all_game_message:
        if not (await send_synchronous_message(F'[{name}] <{player}> {chat_message}')):
            logger.warning('发送消息失败！请检查机器人状态是否正确和群号是否填写正确。')
    if config.sync_message_between_servers:
        await server_manager.broadcast(name, player, chat_message, except_server=name)
    return True


async def player_death(name: str, data: list):
    player, death_message = data
    logger.debug(F'收到玩家死亡 {death_message} 消息！')
    if config.broadcast_player and (not config.bot_prefix or not player.upper().startswith(config.bot_prefix)):
        server_message = F'玩家 {player} 死亡了，呜……'
        if not (await send_synchronous_message(server_message)):
            logger.warning('发送消息失败！请检查机器人状态是否正确和群号是否填写正确。')
        if config.sync_message_between_servers:
            await server_manager.broadcast(name, message=server_message, except_server=name)
    return True


async def player_joined(name: str, player: str):
    logger.info('收到玩家加入服务器通知！')
    if config.broadcast_player:
        server_message = F'玩家 {player} 加入了游戏。'
        group_message = F'玩家 {player} 加入了 [{name}] 服务器，喵～'
        if config.bot_prefix and player.upper().startswith(config.bot_prefix):
            group_message = F'机器人 {player} 加入了 [{name}] 服务器。'
            if config.sync_message_between_servers:
                server_message = F'机器人 {player} 加入了游戏。'
        if config.sync_message_between_servers:
            await server_manager.broadcast(name, message=server_message, except_server=name)
        if await send_synchronous_message(group_message):
            return True
        logger.warning('发送消息失败！请检查机器人状态是否正确和群号是否填写正确。')
        return None
    return True


async def player_left(name: str, player: str):
    logger.info('收到玩家离开服务器通知！')
    if config.broadcast_player:
        server_message = F'玩家 {player} 离开了游戏。'
        group_message = F'玩家 {player} 离开了 [{name}] 服务器，呜……'
        if config.bot_prefix and player.upper().startswith(config.bot_prefix):
            server_message = F'机器人 {player} 离开了游戏。'
            group_message = F'机器人 {player} 离开了 [{name}] 服务器。'
        if config.sync_message_between_servers:
            await server_manager.broadcast(name, message=server_message, except_server=name)
        if await send_synchronous_message(group_message):
            return True
        logger.warning('发送消息失败！请检查机器人状态是否正确和群号是否填写正确。')
        return None
    return True


def setup_websocket_server():
    if isinstance((driver := get_driver()), ASGIMixin):
        server = WebSocketServerSetup(URL('/websocket/bot'), 'bot', handle_websocket_bot)
        driver.setup_websocket_server(server)
        server = WebSocketServerSetup(URL('/websocket/minecraft'), 'minecraft', handle_websocket_minecraft)
        driver.setup_websocket_server(server)
        logger.success('装载 WebSocket 服务器成功！')
        return None
    logger.error('装载 WebSocket 服务器失败！请检查驱动是否正确。')
    exit(1)
