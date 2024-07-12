from pathlib import Path
from json import load, dump

from nonebot.log import logger


class DataManager:
    servers: dict = {}
    server_numbers: list = []
    players: dict = {}
    commands: dict = {}

    data_dir = Path('./Data/')

    def load(self):
        self.load_command_info()
        logger.info('加载数据文件……')
        if not self.data_dir.exists():
            logger.warning('数据文件目录不存在，正在创建数据目录……')
            self.data_dir.mkdir()
        server_file = (self.data_dir / 'Server.json')
        player_file = (self.data_dir / 'Player.json')
        if server_file.exists() and player_file.exists():
            with server_file.open(encoding='Utf-8', mode='r') as file:
                self.servers = load(file)
                self.server_numbers = self.servers.pop('numbers')
            with player_file.open(encoding='Utf-8', mode='r') as file:
                self.players = load(file)
            logger.success('加载数据文件完毕！')
        logger.warning('服务器信息文件不存在，正在创建服务器信息文件……')
        self.save()

    def load_command_info(self):
        logger.info('正在加载命令信息……')
        commands_path = Path('./Plugins/Commands.json')
        if not commands_path.exists():
            logger.error('命令信息文件不存在，请重新安装后再试！')
            exit(1)
        with commands_path.open(encoding='Utf-8', mode='r') as file:
            self.commands = load(file)
        logger.success('加载命令信息完毕！')

    def save(self):
        logger.info('正在保存数据文件……')
        self.servers['numbers'] = self.server_numbers
        server_file = (self.data_dir / 'Server.json')
        player_file = (self.data_dir / 'Player.json')
        with server_file.open(encoding='Utf-8', mode='w') as file:
            dump(self.servers, file)
        with player_file.open(encoding='Utf-8', mode='w') as file:
            dump(self.players, file)
        logger.success('保存数据文件完毕！')

    def append_server(self, name: str, info: list):
        if name not in self.server_numbers:
            self.server_numbers.append(name)
        self.servers[name] = info

    def remove_server(self, name: str):
        self.server_numbers.remove(name)
        self.servers.pop(name)


data_manager = DataManager()
