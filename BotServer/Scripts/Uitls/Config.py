from os.path import exists
from json import loads, load, dump
from dotenv import dotenv_values

from nonebot.log import logger


class Config:
    servers = {}
    players = {}

    token: str = None
    bot_prefix: str = None
    main_group: int = None
    sync_groups: list = None
    command_start: str = None
    command_disabled: list = None

    def __init__(self):
        logger.info('加载配置文件……')
        self.load()
        self.check()
        logger.success('加载配置文件完毕！')

    def load(self):
        data = dotenv_values('.env')
        for key, value in data.items():
            exec(F'self.{key.lower()} = value')
        if exists('Data.json'):
            with open('Data.json', encoding='Utf-8', mode='r') as file:
                content = load(file)
                self.servers = content.get('servers', {})
                self.players = content.get('players', {})
                return None
        logger.info('未发现玩家数据文件！正在生成……')
        self.save()

    def save(self):
        logger.info('正在保存数据文件……')
        content = {'servers': self.servers, 'players': self.players}
        with open('Data.json', encoding='Utf-8', mode='w') as file:
            dump(content, file)

    def check(self):
        for name, type in self.__annotations__.items():
            if not name.startswith('__'):
                if value := eval(F'self.{name}'):
                    if type == int:
                        exec(F'self.{name} = {value}')
                    elif type == list:
                        exec(F'self.{name} = {loads(value)}')
