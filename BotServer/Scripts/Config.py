from pydantic import BaseModel

from nonebot import get_plugin_config


class Config(BaseModel):
    token: str = ''
    bot_prefix: str = None

    superusers: list[str] = []
    command_start: list[str] = ['.']
    command_enabled: list[str] = []

    command_groups: list[int] = []
    message_groups: list[int] = []

    command_minecraft_whitelist: list[str] = []
    command_minecraft_blacklist: list[str] = []

    broadcast_server: bool = True
    broadcast_player: bool = True

    sync_all_qq_message: bool = True
    sync_all_game_message: bool = False
    sync_message_between_servers: bool = True

    server_watcher_max_cache: int = 200
    server_watcher_update_interval: int = 1

    whitelist_command: str = 'whitelist'

    sync_color_source: str = 'gray'
    sync_color_player: str = 'gray'
    sync_color_message: str = 'gray'


config: Config = get_plugin_config(Config)

config.server_watcher_update_interval *= 60
config.bot_prefix = config.bot_prefix.upper()
if config.sync_all_qq_message and ('send' in config.command_enabled):
    config.command_enabled.remove('send')