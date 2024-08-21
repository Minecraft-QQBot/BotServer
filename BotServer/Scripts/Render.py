from pathlib import Path

from nonebot import require

require('nonebot_plugin_htmlrender')
from nonebot_plugin_htmlrender import template_to_pic

template_path = str(Path('Resources/Images/'))


async def render_template(template_name: str, size: tuple, **kwargs):
    width, height = size
    page = {'viewport': {'width': width, 'height': height}, 'base_url': F'file://{template_path}'}
    return await template_to_pic(template_path, template_name, kwargs, page, 5)
