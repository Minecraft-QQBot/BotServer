from .Base import *
from .Remove import *

from nonebot.log import logger

logger.debug('加载命令 Server 完毕！')


try:
    from .Status import *
except ModuleNotFoundError:
    logger.warning('未安装 server status 指令的依赖库，这部分功能将不可用！如若你想使用此命令，请安装依赖库 matplotlib 后重启机器人服务器。')
