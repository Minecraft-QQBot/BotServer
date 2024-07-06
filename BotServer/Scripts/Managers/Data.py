from os.path import exists
from json import load, dump
from typing import Any

from nonebot.log import logger


class DataManager:
    servers: dict = {}
    server_numbers: list = []
    players: dict = {}
    commands: dict = {}

    def load(self):
        self.load_command_info()
        logger.info('加载数据文件……')
        if exists('Data.json'):
            with open('Data.json', encoding='Utf-8', mode='r') as file:
                content = load(file)
                self.servers = content.get('servers', {})
                self.players = content.get('players', {})
                self.server_numbers = self.servers.pop('numbers', [])
                logger.success('加载配置文件完毕！')
                return None
        logger.info('未发现数据文件！正在生成……')
        self.save()

    def load_command_info(self):
        logger.info('正在加载命令信息……')
        with open('Plugins/Commands.json', encoding='Utf-8', mode='r') as file:
            self.commands = load(file)
        logger.success('加载命令信息完毕！')

    def save(self):
        logger.info('正在保存数据文件……')
        self.servers['numbers'] = self.server_numbers
        content = {'servers': self.servers, 'players': self.players}
        with open('Data.json', encoding='Utf-8', mode='w') as file:
            dump(content, file)
        logger.success('保存数据文件完毕！')

    def append_server(self, name: str, info: list):
        if name not in self.server_numbers:
            self.server_numbers.append(name)
        self.servers[name] = info

    def remove_server(self, name: str):
        self.server_numbers.remove(name)
        self.servers.pop(name)


data_manager = DataManager()
