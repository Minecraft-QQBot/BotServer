from hashlib import md5
from json import load, dump
from pathlib import Path
from time import time

from nonebot.log import logger

from ..Config import config


class DataManager:
    # WebUI认证令牌
    webui_token: str = None

    # 服务器列表
    servers: list = []
    # 玩家及其绑定的QQ号
    players: dict = {}
    # 命令数据
    commands: dict = {}

    # 数据目录
    data_dir = Path('Data')

    def load(self):
        """
        加载数据管理器。
        包括加载机器人数据和从数据文件中加载信息。
        如果数据文件不存在，则会创建新的数据文件。
        """
        self.load_bot_data()
        logger.info('加载数据文件……')
        if not self.data_dir.exists():
            logger.warning('数据文件目录不存在，正在创建数据目录……')
            self.data_dir.mkdir()
        count_flag = 0
        webui_file = (self.data_dir / 'Webui.json')
        server_file = (self.data_dir / 'Server.json')
        player_file = (self.data_dir / 'Player.json')
        # 加载WebUI令牌
        if webui_file.exists():
            with webui_file.open(encoding='Utf-8', mode='r') as file:
                count_flag += 1
                self.webui_token = load(file)['token']
        else: self.create_token()
        # 加载服务器列表
        if server_file.exists():
            with server_file.open(encoding='Utf-8', mode='r') as file:
                count_flag += 1
                self.servers = load(file)
        # 加载玩家及其绑定的QQ号
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
        """
        加载机器人命令数据。
        如果数据文件不存在，则记录错误并退出程序。
        """
        logger.debug('正在加载机器人数据……')
        bot_data = Path('Resources/Commands.json')
        if not bot_data.exists():
            logger.error('加载机器人数据失败，请重新安装后再试！')
            exit(1)
        with bot_data.open('r', encoding='Utf-8') as file:
            self.commands = load(file)
        logger.success('加载正在加载机器人数据完毕！')

    def save(self):
        """
        保存数据到相应的JSON文件。
        包括WebUI令牌、服务器列表和玩家绑定信息。
        """
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
        """
        生成新的WebUI认证令牌。
        使用时间戳和固定字符串进行MD5哈希。
        """
        md5_digest = md5()
        md5_digest.update(F'{time()} Webui'.encode('Utf-8'))
        self.webui_token = md5_digest.hexdigest()

    def remove_server(self, name: str):
        """
        从服务器列表中移除指定的服务器并保存更改。

        参数:
        - name: 服务器名称
        """
        self.servers.remove(name)
        self.save()

    def append_server(self, name: str):
        """
        向服务器列表中添加指定的服务器并保存更改。

        参数:
        - name: 服务器名称
        """
        if name not in self.servers:
            self.servers.append(name)
            self.save()

    def append_player(self, user: str, player: str):
        """
        将玩家绑定到指定的QQ号，并根据配置的绑定上限进行检查。

        参数:
        - user: QQ号
        - player: 玩家名称

        返回:
        - bool: 绑定是否成功
        """
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
        """
        从指定的QQ号中移除绑定的玩家。

        参数:
        - user: QQ号
        - player: 玩家名称，如果为None，则移除所有绑定的玩家

        返回:
        - 如果移除成功，返回移除的玩家名称或玩家列表；否则返回False或None。
        """
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
        """
        检查玩家名称是否已被其他QQ号绑定。

        参数:
        - player: 玩家名称

        返回:
        - bool: 玩家名称是否被占用
        """
        player = player.lower()
        for bounded_players in self.players.values():
            if player in (bounded_player.lower() for bounded_player in bounded_players):
                return True
        return False


data_manager = DataManager()
