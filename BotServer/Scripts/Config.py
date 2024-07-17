from pydantic import BaseModel

from nonebot import get_plugin_config


class Config(BaseModel):
    token: str = ''
    bot_prefix: str = ''

    superusers: list[str] = []
    command_start: list[str] = ['.']
    command_enabled: list[str] = []
    command_groups: list[int] = []
    sync_message_groups: list[int] = []

    command_minecraft_whitelist: list[str] = []
    command_minecraft_blacklist: list[str] = []

    broadcast_server: bool = True
    broadcast_player: bool = True

    server_watcher_max_cache: int = 200
    server_watcher_update_interval: int = 1

    whitelist_command: str = 'whitelist'

    source_name_color: str = 'gray'
    qq_player_color: str = 'gray'
    qq_message_color: str = 'gray'


config: Config = get_plugin_config(Config)
