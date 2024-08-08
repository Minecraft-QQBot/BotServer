from hashlib import md5
from json import load, dump
from pathlib import Path
from time import time

from nonebot.log import logger

from ..Config import config


class DataManager:
    webui_token: str = None

    servers: list = []
    players: dict = {}
    commands: dict = {}

    data_dir = Path('Data')

    def load(self):
        self.load_bot_data()
        logger.info('加载数据文件……')
        if not self.data_dir.exists():
            logger.warning('数据文件目录不存在，正在创建数据目录……')
            self.data_dir.mkdir()
        count_flag = 0
        webui_file = (self.data_dir / 'Webui.json')
        server_file = (self.data_dir / 'Server.json')
        player_file = (self.data_dir / 'Player.json')
        if webui_file.exists():
            with webui_file.open(encoding='Utf-8', mode='r') as file:
                count_flag += 1
                self.webui_token = load(file)['token']
        else: self.create_token()
        if server_file.exists():
            with server_file.open(encoding='Utf-8', mode='r') as file:
                count_flag += 1
                self.servers = load(file)
        if player_file.exists():
            with player_file.open(encoding='Utf-8', mode='r') as file:
                count_flag += 1
                self.players = load(file)
        if count_flag == 3:
            logger.success('加载数据文件完毕！')
            return None
        logger.warning('服务器信息文件不存在，正在创建服务器信息文件……')
        self.save()

    def load_bot_data(self):
        logger.debug('正在加载机器人数据……')
        bot_data = Path('Resources/Commands.json')
        if not bot_data.exists():
            logger.error('加载机器人数据失败，请重新安装后再试！')
            exit(1)
        with bot_data.open('r', encoding='Utf-8') as file:
            self.commands = load(file)
        logger.success('加载正在加载机器人数据完毕！')

    def save(self):
        logger.debug('正在保存数据文件……')
        webui_file = (self.data_dir / 'Webui.json')
        server_file = (self.data_dir / 'Server.json')
        player_file = (self.data_dir / 'Player.json')
        with webui_file.open('w', encoding='Utf-8') as file:
            dump({'token': self.webui_token}, file)
        with server_file.open('w', encoding='Utf-8') as file:
            dump(self.servers, file)
        with player_file.open('w', encoding='Utf-8') as file:
            dump(self.players, file)
        logger.success('保存数据文件完毕！')

    def create_token(self):
        md5_digest = md5()
        md5_digest.update(F'{time()} Webui'.encode('Utf-8'))
        self.webui_token = md5_digest.hexdigest()

    def remove_server(self, name: str):
        self.servers.remove(name)
        self.save()

    def append_server(self, name: str):
        if name not in self.servers:
            self.servers.append(name)
            self.save()

    def append_player(self, user: str, player: str):
        if user not in self.players:
            self.players[user] = [player]
            self.save()
            return True
        if config.qq_bound_max_number == 0:
            self.players[user].append(player)
            self.save()
            return True
        if len(self.players[user]) < config.qq_bound_max_number:
            self.players[user].append(player)
            self.save()
            return True
        return False

    def remove_player(self, user: str, player: str = None):
        if not player:
            bounded = self.players.pop(user, None)
            self.save()
            return bounded
        if player in self.players[user]:
            self.players[user].remove(player)
            if not self.players[user]:
                self.players.pop(user)
            self.save()
            return player
        return False

    def check_player_occupied(self, player: str):
        player = player.lower()
        for bounded_players in self.players.values():
            if player in (bounded_player.lower() for bounded_player in bounded_players):
                return True
        return False


data_manager = DataManager()
