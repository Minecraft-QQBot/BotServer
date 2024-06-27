from os.path import exists
from json import load, dump

from nonebot.log import logger


class DataManager:
    servers = {}
    players = {}
    commands = {}

    def load(self):
        self.load_command_info()
        logger.info('加载数据文件……')
        if exists('Data.json'):
            with open('Data.json', encoding='Utf-8', mode='r') as file:
                content = load(file)
                self.servers = content.get('servers', {})
                self.players = content.get('players', {})
                logger.success('加载配置文件完毕！')
                return None
        logger.info('未发现玩家数据文件！正在生成……')
        self.save()

    def load_command_info(self):
        logger.info('正在加载命令信息……')
        with open('Plugins/Commands.json', encoding='Utf-8', mode='r') as file:
            self.commands = load(file)
        logger.success('加载命令信息完毕！')

    def save(self):
        logger.info('正在保存数据文件……')
        content = {'servers': self.servers, 'players': self.players}
        with open('Data.json', encoding='Utf-8', mode='w') as file:
            dump(content, file)
        logger.success('保存数据文件完毕！')


data_manager = DataManager()
