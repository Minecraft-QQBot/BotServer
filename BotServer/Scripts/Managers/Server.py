from .Data import data_manager
from ..Config import config

from typing import Union
from json import dumps, loads
from mcdreforged.api.rcon import RconConnection

from nonebot.log import logger
from nonebot.drivers import WebSocket
from nonebot.exception import WebSocketClosed


class RconServer:
    port: int = None
    name: str = None
    status: bool = False
    rcon: RconConnection = None

    def __init__(self, name: str, info: list):
        self.name = name
        password, self.port = info
        self.rcon = RconConnection('127.0.0.1', self.port, password)

    def connect(self):
        try: flag = self.rcon.connect()
        except ConnectionRefusedError: flag = False
        if not flag:
            logger.warning(F'连接到服务器 [{self.name}] 失败！')
            return None
        self.status = True
        logger.success(F'连接到服务器 [{self.name}] 成功！')
        return True

    def send_command(self, command: str):
        if self.status:
            result = self.rcon.send_command(command, max_retry_time=5)
            if result is None:
                self.status = False
                self.rcon.disconnect()
                logger.error(F'尝试发送指令次数过多，服务器 [{self.name}] 已断开连接！')
                return None
            return result

    async def disconnect(self):
        self.status = False
        self.rcon.disconnect()
        logger.success(F'已断开与服务器 [{self.name}] 的连接！')


class WebsocketServer:
    name: str = None
    status: bool = True
    websocket: WebSocket = None

    def __init__(self, name: str, websocket: WebSocket):
        self.name = name
        self.websocket = websocket

    async def disconnect(self):
        self.status = False
        await self.websocket.close()
        logger.success(F'已断开与服务器 [{self.name}] 的连接！')

    async def send_data(self, type: str, data: dict = {}):
        try:
            await self.websocket.send(dumps({'type': type, 'data': data}))
            logger.debug(F'已向服务器 [{self.name}] 发送数据 {data}，正在等待回应……')
            response = loads(await self.websocket.receive())
            if response.get('success'):
                logger.debug(F'已收到服务器 [{self.name}] 的回应 {response}，数据发送成功！')
                return response
        except (WebSocketClosed, ConnectionError):
            self.status = False
            self.websocket = None
            logger.warning(F'与服务器 [{self.name}] 的连接已断开！')
            return None

    async def send_command(self, command: str):
        return await self.send_data('command', {'command': command})

    async def send_broadcast(self, message: str):
        return await self.send_data('message', {'message': message})

    async def send_player_list(self):
        return await self.send_data('player_list')


class ServerManager:
    server_numbers: list[str] = []
    servers: dict[str, Union[WebsocketServer, RconServer]] = []

    def init(self):
        self.server_numbers = data_manager.server_numbers
        logger.info('初始化服务器管理器！正在尝试连接到已保存的服务器……')
        for name in self.server_numbers:
            info = {'name': name, 'rcon': data_manager.servers.get(name)}
            if (server := self.connect_server(info, False)) and server.status:
                server.send_command('say BotServer was connected to the server!')
        logger.success('服务器管理器初始化完成！')

    def broadcast(self, source: str, player: str = None, message: str = None, except_server: str = None):
        params = [{'color': config.sync_color_source, 'text': F'[{source}] '}]
        if player: params.append({'color': config.sync_color_player, 'text': F'<{player}> '})
        if message: params.append({'color': config.sync_color_message, 'text': message})
        command = F'tellraw @a {dumps(params)}'
        if not except_server:
            self.execute(command)
            return None
        for name, server in self.servers.items():
            if name != except_server and server.status:
                server.send_command(command)

    def execute(self, command: str, server_flag: Union[str, int] = None):
        if not server_flag:
            logger.debug(F'执行命令 [{command}] 到所有已连接的服务器。')
            return {name: server.send_command(command) for name, server in self.servers.items() if server.status}
        if server := self.get_server(server_flag):
            logger.debug(F'执行命令 [{command}] 到服务器 [{server.name}]。')
            return server.send_command(command)

    def get_server(self, server_flag: Union[str, int]):
        if isinstance(server_flag, int) or server_flag.isdigit():
            index = int(server_flag)
            if index > len(self.server_numbers):
                return None
            server_flag = self.server_numbers[index - 1]
        server = self.servers.get(server_flag)
        if isinstance(server, Union[WebsocketServer, RconServer]) and server.status:
            return server

    def connect_server(self, info: dict, update_data: bool = True):
        name = info.get('name')
        rcon = info.get('rcon')
        server = RconServer(name, rcon)
        if server.connect():
            self.servers[name] = server
            if update_data:
                for name, check_server in self.servers.items():
                    if isinstance(check_server, RconServer) and check_server.port == server.port:
                        data_manager.servers.pop(check_server.name)
                        data_manager.servers[server.name] = rcon
                        data_manager.server_numbers[data_manager.server_numbers.index(check_server.name)] = server.name
                        return server
                data_manager.append_server(name, rcon)
                data_manager.save()
        return server

    def disconnect_server(self, name: str):
        if server := self.servers.get(name):
            server.disconnect()

    async def unload(self):
        logger.info('正在断开所有服务器的连接……')
        for server in self.servers.values():
            await server.disconnect()
        logger.success('所有服务器的连接已断开！')


server_manager = ServerManager()
