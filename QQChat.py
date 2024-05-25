from mcdreforged.api.utils import Serializable
from mcdreforged.api.command import SimpleCommandBuilder, GreedyText
from mcdreforged.api.all import PluginServerInterface, CommandContext, CommandSource

import requests
from os.path import exists
from json import dumps


PLUGIN_METADATA = {
    'id': 'qq_chat',
    'version': '1.0.0',
    'description': 'A plugin to chat with qq.',
}


class Config(Serializable):
    # 机器人服务器的端口
    port: int = 8000
    # 服务器名称
    name: str = 'name'
    # 和机器人服务器的 token 一致
    token: str = 'token'
    # 是否播报服务器开启/关闭
    broadcast_server: bool = True
    # 是否播报玩家进入/离开服务器
    broadcast_player: bool = True
    # 可以不用动
    bot_prefix: str = 'bot_'


config: Config = None
request_url: str = 'http://127.0.0.1:{}'


def on_load(server: PluginServerInterface, old):
    def qq(source: CommandSource, content: CommandContext):
        player = 'Console' if source.is_console else source.player
        send_message(F'[{config.name}] <{player}> {content.get("message")}')

    global request_url, config
    config = server.load_config_simple(target_class=Config)
    request_url = request_url.format(config.port)
    server.register_help_message('qq', '发送消息到 QQ 群')
    server.logger.info('正在注册指令……')
    command_builder = SimpleCommandBuilder()
    command_builder.command('!!qq <message>', qq)
    command_builder.arg('message', GreedyText)
    command_builder.register(server)


def on_server_stop(server: PluginServerInterface, old):
    server.logger.info('检测到服务器关闭，正在通知机器人服务器……')
    send_shutdown(server)
    if config.broadcast_server:
        send_message(F'服务器 [{config.name}] 关闭了！喵~')


def on_server_startup(server: PluginServerInterface):
    server.logger.info('检测到服务器开启，正在连接机器人服务器……')
    send_startup(server)
    if config.broadcast_server:
        send_message(F'服务器 [{config.name}] 已经开启辣！喵~')


def on_player_left(server: PluginServerInterface, player: str):
    if config.broadcast_player:
        if player.upper().startswith(config.bot_prefix):
            send_message(F'机器人 {player} 离开了 [{config.name}] 服务器。')
            return
        send_message(F'玩家 {player} 离开了 [{config.name}] 服务器，呜~')


def on_player_joined(server: PluginServerInterface, player: str, info):
    if config.broadcast_player:
        if player.upper().startswith(config.bot_prefix):
            send_message(F'机器人 {player} 加入了 [{config.name}] 服务器！')
            return
        send_message(F'玩家 {player} 加入了 [{config.name}] 服务器！喵~')


def send_message(message: str):
    data = {'token': config.token, 'message': message}
    request = requests.post(F'{request_url}/send_message', data=dumps(data))
    if request.status_code == 200:
        response = request.json()
        return response.get('Success')


def send_startup(server: PluginServerInterface):
    rcon_info = read_rcon_info(server)
    data = {'token': config.token, 'name': config.name, 'rcon': rcon_info}
    request = requests.post(F'{request_url}/server/startup', data=dumps(data))
    if request.status_code == 200:
        response = request.json()
        if response.get('Success'):
            server.logger.info('发送服务器启动消息成功！')
            config.bot_prefix = response.get('bot_prefix')
            return None
    server.logger.error('发送服务器启动消息失败！请检查配置或查看是否启动服务端，然后重试。')


def send_shutdown(server: PluginServerInterface):
    data = {'token': config.token, 'name': config.name}
    request = requests.post(F'{request_url}/server/shutdown', data=dumps(data))
    if request.status_code == 200:
        response = request.json()
        if response.get('Success'):
            server.logger.info('发送服务器关闭消息成功！')
            return None
    server.logger.error('发送服务器关闭消息失败！请检查配置或查看是否启动服务端，然后重试。')


def read_rcon_info(server: PluginServerInterface):
    password, port = None, None
    if not exists('./server/server.properties'):
        server.logger.error('服务器配置文件不存在！请联系管理员求助。')
        return None
    with open('./server/server.properties', encoding='Utf-8', mode='r') as file:
        for line in file.readlines():
            if (not line) or line.startswith('#'):
                continue
            if len(line := line.strip().split('=')) == 2:
                key, value = line
                if key == 'enable-rcon' and value == 'false':
                    server.logger.error('服务器没有开启 Rcon ！请开启 Rcon 后重试。')
                    return None
                port = (int(value) if key == 'rcon.port' else port)
                password = (value if key == 'rcon.password' else password)
    if not (password and port):
        server.logger.error('服务器配置文件中没有找到 Rcon 信息！请检查服务器配置文件后重试。')
        return None
    return password, port
