# 导入异步时间循环库
import asyncio

# 从nonebot框架获取驱动相关函数
from nonebot import get_driver
# 导入WebSocket相关的设置和类
from nonebot.drivers import WebSocketServerSetup, WebSocket, ASGIMixin, URL
# 导入WebSocket关闭异常
from nonebot.exception import WebSocketClosed
# 导入日志记录器
from nonebot.log import logger

# 导入全局变量模块
import Globals
# 导入配置文件解析模块
from ..Config import config
# 导入服务器管理和数据管理模块
from ..Managers import server_manager, data_manager
# 导入JSON处理工具
from ..Utils import Json, send_synchronous_message


# 验证WebSocket连接的合法性
async def verify(websocket: WebSocket):
    """
    验证WebSocket连接的合法性。

    参数:
    - websocket: WebSocket对象

    返回:
    - name: 服务器名称，如果验证失败则返回None
    """
    # 记录WebSocket连接请求
    logger.info('检测到 WebSocket 链接，正在验证身份……')
    # 获取请求头中的info字段
    if info := websocket.request.headers.get('info'):
        # 解析info字段中的JSON数据
        info = Json.decode(info)
        name = info.get('name')
        # 验证令牌和服务器名称
        if info.get('token') != config.token or (not name):
            # 验证失败，关闭连接
            await websocket.close()
            logger.warning('身份验证失败！请检查插件配置文件是否正确。')
            return None
        # 验证成功，记录日志并返回服务器名称
        logger.success(F'身份验证成功，服务器 [{name}] 已连接到！连接已建立。')
        return name


# 处理与Minecraft服务器相关的WebSocket连接
async def handle_websocket_minecraft(websocket: WebSocket):
    """
    处理与Minecraft服务器相关的WebSocket连接。

    参数:
    - websocket: WebSocket对象
    """
    # 接受WebSocket连接
    await websocket.accept()
    # 验证连接的合法性
    if name := await verify(websocket):
        # 初始化计时器和数据管理器
        time_count = 0
        data_manager.append_server(name)
        server = server_manager.append_server(name, websocket)
        Globals.cpu_occupation[name] = []
        Globals.ram_occupation[name] = []
        # 循环检测服务器状态
        while True:
            await asyncio.sleep(30)
            if not server.is_connected: break
            if server.type != 'FakePlayer':
                time_count += 1
                if time_count <= config.server_memory_update_interval:
                    continue
                logger.debug(F'正在尝试获取服务器 [{name}] 的占用数据！')
                # 获取服务器资源占用数据
                if data := await server.send_server_occupation():
                    time_count = 0
                    cpu, ram = data
                    Globals.cpu_occupation[name].append(cpu)
                    Globals.ram_occupation[name].append(ram)
                    if len(Globals.cpu_occupation[name]) > config.server_memory_max_cache:
                        Globals.cpu_occupation[name].pop(0)
                        Globals.ram_occupation[name].pop(0)
        # 清理过期数据
        Globals.cpu_occupation.pop(name, None)
        Globals.ram_occupation.pop(name, None)
        logger.info(F'检测到连接与 [{name}] 已断开！移除此服务器内存数据。')


# 处理与机器人相关的WebSocket连接
async def handle_websocket_bot(websocket: WebSocket):
    """
    处理与机器人相关的WebSocket连接。

    参数:
    - websocket: WebSocket对象
    """
    # 接受WebSocket连接
    await websocket.accept()
    # 验证连接的合法性
    if name := await verify(websocket):
        try:
            while True:
                response = None
                receive_message = Json.decode(await websocket.receive())
                if receive_message is None:
                    continue
                data = receive_message.get('data')
                event_type = receive_message.get('type')
                # 根据消息类型处理不同的事件
                if event_type == 'message':
                    response = await message(name, data)
                elif event_type == 'server_startup':
                    response = await server_startup(name, data)
                elif event_type == 'server_shutdown':
                    response = await server_shutdown(name, data)
                elif event_type == 'player_death':
                    response = await player_death(name, data)
                elif event_type == 'player_left':
                    response = await player_left(name, data)
                elif event_type == 'player_joined':
                    response = await player_joined(name, data)
                elif event_type == 'player_chat':
                    # 若是聊天信息，则不等待回应。
                    await player_chat(name, data)
                    continue
                if response is not None:

                    # 调试日志，记录接收到的数据
                    logger.debug(F'对来自 [{name}] 的数据 {receive_message}')
                    if response is True:
                        await websocket.send(Json.encode({'success': True}))
                        continue
                    await websocket.send(Json.encode({'success': True, 'data': response}))
                    continue
                # 警告日志，记录无法解析的数据
                logger.warning(F'收到来自 [{name}] 无法解析的数据 {receive_message}')
                await websocket.send(Json.encode({'success': False}))
                # 处理WebSocket连接关闭的异常
        except (ConnectionError, WebSocketClosed):
            logger.info('WebSocket 连接已关闭！')


# 异步函数，处理消息发送
async def message(name: str, group_message: str):
    # 检查群消息是否为空
    if group_message:
        # 调试日志，记录将要发送的消息
        logger.debug(F'发送消息 {group_message} 到消息群！')
        # 发送同步消息，并根据结果返回True或None
        if await send_synchronous_message(group_message):
            return True
    # 警告日志，发送消息失败
    logger.warning('发送消息失败！请检查机器人状态是否正确和群号是否填写正确。')
    return None


# 异步函数，处理服务器启动事件
async def server_startup(name: str, data: dict):
    # 信息日志，记录服务器启动数据接收
    logger.info('收到服务器开启数据！尝试连接到服务器……')
    # 添加服务器到数据管理器
    data_manager.append_server(name)
    # 根据配置广播服务器开启消息
    if config.sync_message_between_servers:
        await server_manager.broadcast(name, message='服务器已开启！', except_server=name)
    # 根据配置发送服务器开启消息到群
    if config.broadcast_server:
        if await send_synchronous_message(F'服务器 [{name}] 已开启，喵～'):
            return config.sync_all_game_message
        # 警告日志，发送消息失败
        logger.warning('发送消息失败！请检查机器人状态是否正确和群号是否填写正确。')
        return None
    return config.sync_all_game_message


# 异步函数，处理服务器关闭事件
async def server_shutdown(name: str, data: dict):
    # 信息日志，记录服务器关闭数据接收
    logger.info('收到服务器关闭信息！正在断开连接……')
    # 断开服务器连接
    await server_manager.disconnect_server(name)
    # 根据配置广播服务器关闭消息
    if config.sync_message_between_servers:
        await server_manager.broadcast(name, message='服务器已关闭！', except_server=name)
    # 根据配置发送服务器关闭消息到群
    if config.broadcast_server:
        if await send_synchronous_message(F'服务器 [{name}] 已关闭，呜……'):
            return True
        # 警告日志，发送消息失败
        logger.warning('发送消息失败！请检查机器人状态是否正确和群号是否填写正确。')
        return None
    return True


# 异步函数，处理玩家死亡事件
async def player_death(name: str, data: list):
    # 解析玩家和死亡消息
    player, death_message = data
    # 调试日志，记录玩家死亡消息
    logger.debug(F'收到玩家死亡 {death_message} 消息！')
    # 根据配置和玩家前缀判断是否广播玩家死亡消息
    if (not config.bot_prefix) or (not player.upper().startswith(config.bot_prefix)):
        broadcast_message = F'玩家 {player} 死亡了，呜……'
        if config.sync_message_between_servers:
            await server_manager.broadcast(name, message=broadcast_message, except_server=name)
        if config.broadcast_player:
            if await send_synchronous_message(broadcast_message):
                return True
            # 警告日志，发送消息失败
            logger.warning('发送消息失败！请检查机器人状态是否正确和群号是否填写正确。')
            return False
    return True


# 异步函数，处理玩家加入事件
async def player_joined(name: str, player: str):
    # 信息日志，记录玩家加入服务器通知
    logger.info('收到玩家加入服务器通知！')
    # 构造服务器和群消息
    server_message = F'玩家 {player} 加入了游戏。'
    group_message = F'玩家 {player} 加入了 [{name}] 服务器，喵～'
    # 根据配置和玩家前缀调整消息内容
    if config.bot_prefix and player.upper().startswith(config.bot_prefix):
        group_message = F'机器人 {player} 加入了 [{name}] 服务器。'
        server_message = F'机器人 {player} 加入了游戏。'
    # 根据配置广播玩家加入消息
    if config.sync_message_between_servers:
        await server_manager.broadcast(name, message=server_message, except_server=name)
    if config.broadcast_player:
        if await send_synchronous_message(group_message):
            return True
        # 警告日志，发送消息失败
        logger.warning('发送消息失败！请检查机器人状态是否正确和群号是否填写正确。')
        return None
    return True


# 异步函数，处理玩家离开事件
async def player_left(name: str, player: str):
    # 信息日志，记录玩家离开服务器通知
    logger.info('收到玩家离开服务器通知！')
    # 构造服务器和群消息
    server_message = F'玩家 {player} 离开了游戏。'
    group_message = F'玩家 {player} 离开了 [{name}] 服务器，呜……'
    # 根据配置和玩家前缀调整消息内容
    if config.bot_prefix and player.upper().startswith(config.bot_prefix):
        server_message = F'机器人 {player} 离开了游戏。'
        group_message = F'机器人 {player} 离开了 [{name}] 服务器。'
    # 根据配置广播玩家离开消息
    if config.sync_message_between_servers:
        await server_manager.broadcast(name, message=server_message, except_server=name)
    if config.broadcast_player:
        if await send_synchronous_message(group_message):
            return True
        # 警告日志，发送消息失败
        logger.warning('发送消息失败！请检查机器人状态是否正确和群号是否填写正确。')
        return None
    return True


# 异步函数，处理玩家聊天事件
async def player_chat(name: str, data: list):
    # 解析玩家和聊天消息
    player, chat_message = data
    # 调试日志，记录玩家聊天消息
    logger.debug(F'收到玩家 {player} 在服务器 [{name}] 发送消息！')
    # 根据配置同步所有游戏消息到群
    if config.sync_all_game_message:
        if not (await send_synchronous_message(F'[{name}] <{player}> {chat_message}')):
            # 警告日志，发送消息失败
            logger.warning('发送消息失败！请检查机器人状态是否正确和群号是否填写正确。')
    # 根据配置在服务器间同步消息
    if config.sync_message_between_servers:
        await server_manager.broadcast(name, player, chat_message, except_server=name)


# 函数，设置WebSocket服务器
def setup_websocket_server():
    # 检查并设置WebSocket服务器
    if isinstance((driver := get_driver()), ASGIMixin):
        server = WebSocketServerSetup(URL('/websocket/bot'), 'bot', handle_websocket_bot)
        driver.setup_websocket_server(server)
        server = WebSocketServerSetup(URL('/websocket/minecraft'), 'minecraft', handle_websocket_minecraft)
        driver.setup_websocket_server(server)
        # 成功日志，WebSocket服务器设置成功
        logger.success('装载 WebSocket 服务器成功！')
        return None
    # 错误日志，WebSocket服务器设置失败
    logger.error('装载 WebSocket 服务器失败！请检查驱动是否正确。')
    exit(1)
