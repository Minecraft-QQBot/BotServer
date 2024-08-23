from nonebot import get_plugin_config
from pydantic import BaseModel


class Config(BaseModel):
    port: int = 8000
    onebot_access_token: str = ''

    token: str = ''
    bot_prefix: str = None
    admin_superusers: bool = True

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

    server_memory_max_cache: int = 200
    server_memory_update_interval: int = 1

    whitelist_command: str = 'whitelist'

    sync_color_source: str = 'gray'
    sync_color_player: str = 'gray'
    sync_color_message: str = 'gray'

    qq_bound_max_number: int = 1

    ai_enabled: bool = False
    ai_api_key: str = None
    ai_role_message: str = None

    image_mode: bool = False
    image_background: str = None

    auto_reply: bool = False
    auto_reply_keywords: dict = None


config: Config = get_plugin_config(Config)

config.server_memory_update_interval *= 2
config.bot_prefix = config.bot_prefix.upper()
config.sync_color_source = config.sync_color_source.lower()
config.sync_color_player = config.sync_color_player.lower()
config.sync_color_message = config.sync_color_message.lower()
config.command_enabled.append('about')
if config.sync_all_qq_message and ('send' in config.command_enabled):
    config.command_enabled.remove('send')
