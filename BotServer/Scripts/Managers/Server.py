from .Data import data_manager
from Scripts.Config import config

from json import dumps
from typing import Union
from mcdreforged.api.rcon import RconConnection

from nonebot.log import logger


class ServerManager:
    status: dict[str, bool] = {}
    servers: dict[str, RconConnection] = {}

    def init(self):
        logger.info('初始化服务器管理器！正在尝试连接到已保存的服务器……')
        for name, info in data_manager.servers.items():
            if name != 'numbers':
                if self.connect_server({'name': name, 'rcon': info}, False):
                    self.execute('say BotServer was connected to the server!', name)
        logger.success('服务器管理器初始化完成！')

    def unload(self):
        logger.info('正在断开所有服务器的连接……')
        for rcon in self.servers.values():
            rcon.disconnect()
        logger.success('所有服务器的连接已断开！')

    def broadcast(self, source: str, player: str = None, message: str = None, except_server: str = None):
        params = [{'color': config.sync_color_source, 'text': F'[{source}] '}]
        if player: params.append({'color': config.sync_color_player, 'text': F'<{player}> '})
        if message: params.append({'color': config.sync_color_message, 'text': message})
        params = dumps(params)
        if not except_server:
            self.execute(F'tellraw @a {params}')
            return None
        for name, status in self.status.items():
            if name != except_server and status:
                self.servers[name].send_command(F'tellraw @a {params}')

    def execute(self, command: str, server: Union[str, int] = None):
        if not server:
            result = {}
            logger.debug(F'执行命令 [{command}] 到所有已连接的服务器。')
            for name, rcon in self.servers.items():
                if self.status.get(name):
                    result[name] = rcon.send_command(command)
            return result
        if name := self.parse_server(server):
            logger.debug(F'执行命令 [{command}] 到服务器 [{name}]。')
            rcon = self.servers.get(name)
            return rcon.send_command(command)

    def parse_server(self, server: Union[str, int]):
        if isinstance(server, int) or server.isdigit():
            server = int(server)
            if server > len(data_manager.server_numbers):
                return None
            server = data_manager.server_numbers[server - 1]
        return server if self.status.get(server) else None

    def connect_server(self, info: dict, update: bool = True):
        name = info.get('name')
        password, port = info.get('rcon')
        try:
            rcon = RconConnection('127.0.0.1', port, password)
            rcon.connect()
        except ConnectionRefusedError:
            logger.warning(F'连接到服务器 [{name}] 失败！')
            return None
        self.status[name] = True
        self.servers[name] = rcon
        if update is True:
            data_manager.append_server(name, (password, port))
            data_manager.save()
        logger.success(F'连接到服务器 [{name}] 成功！')
        return True

    def disconnect_server(self, name: str):
        if rcon := self.servers.get(name):
            rcon.disconnect()
            self.status[name] = False


server_manager = ServerManager()
