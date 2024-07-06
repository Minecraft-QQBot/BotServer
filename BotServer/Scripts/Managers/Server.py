from Scripts.Managers.Data import data_manager

from json import dumps
from mcdreforged.api.rcon import RconConnection

from nonebot.log import logger


class ServerManager:
    status: dict[str, bool] = {}
    servers: dict[str, RconConnection] = {}

    def init(self):
        logger.info('初始化服务器管理器！正在尝试连接到已保存的服务器……')
        for name, info in data_manager.servers.items():
            if name != 'numbers':
                self.connect_server({'name': name, 'rcon': info})
        logger.success('服务器管理器初始化完成！')

    def unload(self):
        logger.info('正在断开所有服务器的连接……')
        for rcon in self.servers.values():
            rcon.disconnect()
        logger.success('所有服务器的连接已断开！')

    def broadcast(self, text, color='white'):
        params = {'color': color, 'text': text}
        self.execute(F'tellraw @a {dumps(params)}')

    def execute(self, command: str, server: (str | int) = None):
        if server is None:
            result = {}
            for name, rcon in self.servers.items():
                if self.status.get(name):
                    result.setdefault(name, rcon.send_command(command))
            return result
        if name := self.parse_server(server):
            rcon = self.servers.get(name)
            return rcon.send_command(command)
        
    def parse_server(self, server: (str | int)):
        if isinstance(server, int) or server.isdigit():
            server = int(server)
            if server > len(data_manager.server_numbers):
                return None
            server = data_manager.server_numbers[server - 1]
        return server if self.status.get(server) else None

    def connect_server(self, info: dict):
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
        data_manager.append_server(name, (password, port))
        data_manager.save()
        logger.success(F'连接到服务器 [{name}] 成功！')

    def disconnect_server(self, name: str):
        if rcon := self.servers.get(name):
            rcon.disconnect()
            self.status[name] = False


server_manager = ServerManager()
