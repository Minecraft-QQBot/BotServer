# 导入路径处理模块
from pathlib import Path

# 导入nonebot的require函数，用于动态加载插件
from nonebot import require
# 导入酷Q机器人适应层的MessageSegment类，用于构造消息段
from nonebot.adapters.onebot.v11 import MessageSegment

# 导入当前插件的配置类
from .Config import config

# 动态加载nonebot的HTML渲染插件
require('nonebot_plugin_htmlrender')
# 导入HTML渲染工具，用于将模板转换为图片
from nonebot_plugin_htmlrender import template_to_pic

# 定义模板路径，指向资源文件夹下的Images目录
template_path = str(Path('Resources/Images/').absolute())


# 定义一个异步函数，用于渲染模板并返回图片消息段
async def render_template(template_name: str, size: tuple, **kwargs):
    """
    渲染指定模板为图片，并返回图片消息段。

    :param template_name: 模板名称
    :param size: 图片尺寸（宽度，高度）
    :param kwargs: 其他模板参数
    :return: 图片消息段
    """
    # 解构尺寸元组为宽度和高度
    width, height = size
    # 设置模板背景，默认使用配置文件中的背景设置
    kwargs.setdefault('background', config.image_background)
    # 构造页面配置，包括视口尺寸和基础URL
    page = {'viewport': {'width': width, 'height': height}, 'base_url': 'file://' + template_path}
    # 使用模板渲染图片
    image = await template_to_pic(template_path, template_name, kwargs, pages=page, wait=5)
    # 返回图片消息段
    return MessageSegment.image(image)
