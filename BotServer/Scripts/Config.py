from nonebot import get_plugin_config

from pydantic import BaseModel


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


config: Config = get_plugin_config(Config)
