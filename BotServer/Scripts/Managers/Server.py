from typing import Union

from nonebot.drivers import WebSocket
from nonebot.exception import WebSocketClosed
from nonebot.log import logger

from .Data import data_manager
from ..Config import config
from ..Utils import Json


class Server:
    name: str = None
    type: str = None
    status: bool = True
    websocket: WebSocket = None

    def __init__(self, name: str, websocket: WebSocket):
        self.name = name
        self.websocket = websocket
        self.type = websocket.request.headers.get('type')

    async def disconnect(self):
        self.status = False
        await self.websocket.close()
        logger.success(F'已断开与服务器 [{self.name}] 的连接！')

    async def send_data(self, event_type: str, data: object = None, wait: bool = True):
        try:
            message_data = {'type': event_type}
            if data is not None:
                message_data['data'] = data
            await self.websocket.send(Json.encode(message_data))
            if wait is True:
                logger.debug(F'已向服务器 [{self.name}] 发送数据 {message_data}，正在等待回应……')
                response = Json.decode(await self.websocket.receive())
                if response.get('success'):
                    logger.debug(F'已收到服务器 [{self.name}] 的回应 {response}，数据发送成功！')
                    return response.get('data')
                logger.debug(F'向服务器 [{self.name}] 发送数据 {event_type} 失败！')
                return None
            logger.debug(F'向服务器 [{self.name}] 发送数据 {message_data}')
        except (WebSocketClosed, ConnectionError):
            self.status = False
            logger.warning(F'与服务器 [{self.name}] 的连接已断开！')
            return None

    async def send_command(self, command: str):
        return await self.send_data('command', command)

    async def send_message(self, message_data: list):
        await self.send_data('message', message_data, wait=False)

    async def send_mcdr_command(self, command: str):
        return await self.send_data('mcdr_command', command)

    async def send_player_list(self):
        return await self.send_data('player_list')

    async def send_server_occupation(self):
        if data := await self.send_data('server_occupation'):
            return tuple(round(percent, 2) for percent in data)


class ServerManager:
    servers: dict[str, Server] = {}

    def check_online(self):
        return any(server.status for server in self.servers.values())

    def append_server(self, name: str, websocket: WebSocket):
        server = Server(name, websocket)
        self.servers[name] = server
        return server

    def get_server(self, server_flag: Union[str, int]):
        if isinstance(server_flag, int) or server_flag.isdigit():
            index = int(server_flag)
            if index > len(data_manager.servers):
                return None
            server_flag = data_manager.servers[index - 1]
        if (server := self.servers.get(server_flag)) and server.status:
            return server

    async def disconnect_server(self, name: str):
        if server := self.servers.get(name):
            await server.disconnect()

    async def unload(self):
        logger.info('正在断开所有服务器的连接……')
        for server in self.servers.values():
            await server.disconnect()
        logger.success('所有服务器的连接已断开！')

    async def execute(self, command: str):
        logger.debug(F'执行命令 [{command}] 到所有已连接的服务器。')
        return {name: await server.send_command(command) for name, server in self.servers.items() if server.status}

    async def execute_mcdr(self, command: str):
        logger.debug(F'执行命令 [{command}] 到所有已连接的服务器。')
        return {name: await server.send_mcdr_command(command) for name, server in self.servers.items() if
                server.status and server.type == 'McdReforged'}

    async def get_server_occupation(self):
        logger.debug('获取所有已连接服务器的占用率。')
        return {name: await server.send_server_occupation() for name, server in self.servers.items() if server.status}

    async def broadcast(self, source: str, player: str = None, message: str = None, except_server: str = None):
        message_data = [{'color': config.sync_color_source, 'text': F'[{source}] '}]
        if player: message_data.append({'color': config.sync_color_player, 'text': F'<{player}> '})
        if message: message_data.append({'color': config.sync_color_message, 'text': message})
        for name, server in self.servers.items():
            if ((except_server is None) or name != except_server) and server.status:
                await server.send_message(message_data)


server_manager = ServerManager()
