from .Data import data_manager
from ..Config import config

from json import dumps
from typing import Union
from mcdreforged.api.rcon import RconConnection

from nonebot.log import logger


class Server:
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

    def disconnect(self):
        self.status = False
        self.rcon.disconnect()
        logger.success(F'已断开与服务器 [{self.name}] 的连接！')

    def execute(self, command: str):
        if self.status:
            result = self.rcon.send_command(command, max_retry_time=5)
            if result is None:
                self.status = False
                self.rcon.disconnect()
                logger.error(F'尝试发送指令次数过多，服务器 [{self.name}] 已断开连接！')
                return None
            return result


class ServerManager:
    servers: list[Server] = []
    server_numbers: list[str] = []

    def init(self):
        self.server_numbers = data_manager.server_numbers
        logger.info('初始化服务器管理器！正在尝试连接到已保存的服务器……')
        for name in self.server_numbers:
            info = {'name': name, 'rcon': data_manager.servers.get(name)}
            if (server := self.connect_server(info, False)) and server.status:
                server.execute('say BotServer was connected to the server!')
        logger.success('服务器管理器初始化完成！')

    def unload(self):
        logger.info('正在断开所有服务器的连接……')
        for server in self.servers:
            server.disconnect()
        logger.success('所有服务器的连接已断开！')

    def broadcast(self, source: str, player: str = None, message: str = None, except_server: str = None):
        params = [{'color': config.sync_color_source, 'text': F'[{source}] '}]
        if player: params.append({'color': config.sync_color_player, 'text': F'<{player}> '})
        if message: params.append({'color': config.sync_color_message, 'text': message})
        command = F'tellraw @a {dumps(params)}'
        if not except_server:
            self.execute(command)
            return None
        for server in self.servers:
            if server.name != except_server and server.status:
                server.execute(command)

    def execute(self, command: str, server_flag: Union[str, int] = None):
        if not server_flag:
            logger.debug(F'执行命令 [{command}] 到所有已连接的服务器。')
            return {server.name: server.execute(command) for server in self.servers if server.status}
        if server := self.get_server(server_flag):
            logger.debug(F'执行命令 [{command}] 到服务器 [{server.name}]。')
            return server.execute(command)

    def get_server(self, server_flag: Union[str, int]):
        if isinstance(server_flag, int) or server_flag.isdigit():
            index = int(server_flag)
            if index > len(self.servers):
                return None
            server = self.servers[index - 1]
        if server_flag in self.server_numbers:
            server = self.servers[self.server_numbers.index(server_flag)]
        if isinstance(server, Server) and server.status:
            return server

    def connect_server(self, info: dict, update_data: bool = True):
        name = info.get('name')
        rcon = info.get('rcon')
        server = Server(name, rcon)
        if server.connect() and update_data:
            for index, check_server in enumerate(self.servers):
                if check_server.port == server.port:
                    self.servers[index] = server
                    data_manager.servers[name] = rcon
                    data_manager.server_numbers[index] = server.name
                    return server
            data_manager.append_server(name, rcon)
            data_manager.save()
        self.servers.append(server)
        return server

    def disconnect_server(self, name: str):
        if server := self.get_server(name):
            server.disconnect()


server_manager = ServerManager()
