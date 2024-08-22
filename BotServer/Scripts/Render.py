from pathlib import Path

from nonebot import require
from nonebot.adapters.onebot.v11 import MessageSegment

from .Config import config

require('nonebot_plugin_htmlrender')
from nonebot_plugin_htmlrender import template_to_pic

template_path = str(Path('Resources/Images/').absolute())


async def render_template(template_name: str, size: tuple, **kwargs):
    width, height = size
    kwargs.setdefault('background', config.image_background)
    page = {'viewport': {'width': width, 'height': height}, 'base_url': 'file://' + template_path}
    image = await template_to_pic(template_path, template_name, kwargs, pages=page, wait=5)
    return MessageSegment.image(image)
