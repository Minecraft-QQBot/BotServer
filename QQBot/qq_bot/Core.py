from mcdreforged.api.utils import Serializable
from mcdreforged.api.command import SimpleCommandBuilder, GreedyText
from mcdreforged.api.all import PluginServerInterface, CommandContext, CommandSource, Info

import requests
from json import dumps
from pathlib import Path


class Config(Serializable):
    # 机器人服务器的端口
    port: int = 8000
    # 服务器名称
    name: str = 'name'
    # 和机器人服务器的 token 一致
    token: str = 'YourToken'
    sync_all_messages: bool = False


class EventSender:
    server: PluginServerInterface = None
    request_url: str = 'http://127.0.0.1:{}'

    def __init__(self, server: PluginServerInterface, port: int):
        self.server = server
        self.request_url = self.request_url.format(port)

    def __request(self, name: str, data: dict):
        data['name'] = config.name
        data['token'] = config.token
        try:
            request = requests.post(F'{self.request_url}/{name}', data=dumps(data), timeout=10)
        except Exception:
            return None
        if request.status_code == 200:
            response = request.json()
            if response.get('success'):
                return response

    def send_info(self):
        pid = self.server.get_server_pid_all()[-1]
        if self.__request('server/info', {'pid': pid}):
            self.server.logger.info('发送服务器信息成功！')
            return None
        self.server.logger.error('发送服务器信息失败！请检查配置或查看是否启动服务端，然后重试。')

    def send_message(self, message: str):
        data = {'message': message}
        self.server.logger.info(F'向 QQ 群发送消息 {message}')
        return self.__request('send_message', data)

    def send_startup(self):
        if rcon_info := self.read_rcon_info():
            pid = self.server.get_server_pid_all()[-1]
            if response := self.__request('server/startup', {'rcon': rcon_info, 'pid': pid}):
                self.server.logger.info('发送服务器启动消息成功！')
                config.sync_all_messages = response.get('sync_all_messages')
                self.server.save_config_simple(config)
                return None
            self.server.logger.error('发送服务器启动消息失败！请检查配置或查看是否启动服务端，然后重试。')

    def send_shutdown(self):
        if self.__request('server/shutdown', {}):
            self.server.logger.info('发送服务器关闭消息成功！')
            return None
        self.server.logger.error('发送服务器关闭消息失败！请检查配置或查看是否启动服务端，然后重试。')

    def send_player_info(self, player: str, message: str):
        data = {'player': player, 'message': message}
        if self.__request('player/info', data):
            self.server.logger.info(F'发送玩家 {player} 消息 {message} 成功！')
            return None
        self.server.logger.error(F'发送玩家 {player} 消息 {message} 失败！请检查配置或查看是否启动服务端，然后重试。')

    def send_player_left(self, player: str):
        if self.__request('player/left', {'player': player}):
            self.server.logger.info(F'发送玩家 {player} 离开消息成功！')
            return None
        self.server.logger.error(F'发送玩家 {player} 离开消息失败！请检查配置或查看是否启动服务端，然后重试。')

    def send_player_joined(self, player: str):
        if self.__request('player/joined', {'player': player}):
            self.server.logger.info(F'发送玩家 {player} 加入消息成功！')
            return None
        self.server.logger.error(F'发送玩家 {player} 加入消息失败！请检查配置或查看是否启动服务端，然后重试。')

    def read_rcon_info(self):
        password, port = None, None
        server_config = Path('./server/server.properties')
        if not server_config.exists():
            self.server.logger.error('服务器配置文件不存在！请联系管理员求助。')
            return None, None
        with server_config.open('r', encoding='utf-8') as file:
            for line in file.readlines():
                if (not line) or line.startswith('#'):
                    continue
                if len(line := line.strip().split('=')) == 2:
                    key, value = line
                    if key == 'enable-rcon' and value == 'false':
                        self.server.logger.error('服务器没有开启 Rcon ！请开启 Rcon 后重试。')
                        return None
                    port = (int(value) if key == 'rcon.port' else port)
                    password = (value if key == 'rcon.password' else password)
        if not (password and port):
            self.server.logger.error('服务器配置文件中没有找到 Rcon 信息！请检查服务器配置文件后重试。')
            return None, None
        return password, port


config: Config = None
event_sender: EventSender = None


def on_load(server: PluginServerInterface, old):
    def qq(source: CommandSource, content: CommandContext):
        if config.sync_all_messages:
            source.reply('§7已启用 同步所有消息 功能！此指令已自动禁用。§7')
            return None
        player = 'Console' if source.is_console else source.player
        success = event_sender.send_message(F'[{config.name}] <{player}> {content.get("message")}')
        source.reply('§a发送消息成功！§a' if success else '§c发送消息失败！§c')

    global event_sender, config
    config = server.load_config_simple(target_class=Config)
    server.register_help_message('qq', '发送消息到 QQ 群')
    server.logger.info('正在注册指令……')
    command_builder = SimpleCommandBuilder()
    command_builder.command('!!qq <message>', qq)
    command_builder.arg('message', GreedyText)
    command_builder.register(server)
    event_sender = EventSender(server, config.port)


def on_info(server: PluginServerInterface, info: Info):
    if not info.is_player and '[Rcon] BotServer was connected to the server!' in info.content:
        event_sender.send_info()


def on_server_stop(server: PluginServerInterface, old):
    server.logger.info('检测到服务器关闭，正在通知机器人服务器……')
    event_sender.send_shutdown()


def on_server_startup(server: PluginServerInterface):
    server.logger.info('检测到服务器开启，正在连接机器人服务器……')
    event_sender.send_startup()


def on_user_info(server: PluginServerInterface, info: Info):
    event_sender.send_player_info(info.player, info.content)


def on_player_left(server: PluginServerInterface, player: str):
    event_sender.send_player_left(player)


def on_player_joined(server: PluginServerInterface, player: str, info):
    event_sender.send_player_joined(player)
