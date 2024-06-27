from Scripts.Managers.Data import data_manager

from json import dumps
from mcdreforged.api.rcon import RconConnection

from nonebot.log import logger


class ServerManager:
    numbers: list[int] = []
    status: dict[str, bool] = {}
    servers: dict[str, RconConnection] = {}

    def init(self):
        logger.info('初始化服务器管理器！正在尝试连接到已保存的服务器……')
        for name, info in data_manager.servers.items():
            self.connect_server({'name': name, 'rcon': info})
        logger.success('服务器管理器初始化完成！')

    def unload(self):
        for rcon in self.servers.values():
            rcon.disconnect()

    def broadcast(self, text, color='white'):
        params = {'color': color, 'text': text}
        self.execute(F'tellraw @a {dumps(params)}')

    def execute(self, command: str, server_name: (str | int) = None):
        if server_name is None:
            result = {}
            for name, rcon in self.servers.items():
                if self.status.get(name):
                    result.setdefault(name, rcon.send_command(command))
            return result
        if isinstance(server_name, int):
            if len(self.numbers) < server_name:
                return None
            server_name = self.numbers[server_name]
        if self.status.get(name) and (client := self.servers.get(server_name)):
            return client.run(command)

    def connect_server(self, info: dict):
        name = info.get('name')
        password, port = info.get('rcon')
        if name not in self.numbers:
            self.numbers.append(name)
        data_manager.servers[name] = [password, port]
        data_manager.save()
        try:
            rcon = RconConnection('127.0.0.1', port, password)
            rcon.connect()
            self.status[name] = True
            self.servers[name] = rcon
            logger.success(F'连接到服务器 {name} 成功！')
        except ConnectionRefusedError:
            logger.warning(F'连接到服务器 {name} 失败！')

    def disconnect_server(self, name):
        if rcon := self.servers.get(name):
            rcon.disconnect()
            self.status[name] = False


server_manager = ServerManager()
