from Config import config

from json import dumps
from rcon.source import Client

from nonebot.log import logger


class ServerManager:
    status = {}
    servers = {}
    numbers = []

    def __init__(self):
        logger.info('初始化服务器管理器！正在尝试连接到已保存的服务器……')
        for name, info in config.servers.items():
            self.connect_server({'name': name, 'rcon': info})
        logger.success('服务器管理器初始化完成！')

    def say(self, text, color='white'):
        params = {'color': color, 'text': text}
        self.execute(F'tellraw @a {dumps(params)}')

    def execute(self, command: str, server_name: (str | int) = None):
        if server_name is None:
            result = {}
            for name, client in self.servers.items():
                if self.status.get(name):
                    result.setdefault(name, client.run(command))
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
        config.servers[name] = [password, port]
        config.save()
        try:
            client = Client('127.0.0.1', port)
            client.connect(login=True)
            client.login(passwd=password)
            self.status[name] = True
            self.servers[name] = client
            logger.info(F'连接到服务器 {name} 成功！')
        except ConnectionRefusedError:
            logger.warning(F'连接到服务器 {name} 失败！')

    def disconnect_server(self, name):
        if client := self.servers.get(name):
            client.close()
            self.status[name] = False
