from importlib import util

from nonebot.log import logger

from Scripts.Config import config

uuid_caches: dict[str, str] = {}
cpu_occupation: dict[str, list] = {}
ram_occupation: dict[str, list] = {}

openai = None
render_template = None

if config.ai_enabled:
    if util.find_spec('openai') is None:
        logger.error('你已开启 Ai 功能，但却没有安装 OpenAi 库！请先安装后再启动。')
        exit(1)
if config.image_mode:
    if util.find_spec('nonebot_plugin_htmlrender') is None:
        logger.error('你已开启图片模式，但却没有安装对应的库！请先安装后再启动。')
        exit(1)

# LtNsttMj1tUSaieZRjvHHk2h2AZOEKIG
# https://crafatar.com/avatars/{uuid}
