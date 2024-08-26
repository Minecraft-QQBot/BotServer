# 导入路径处理模块
from pathlib import Path
# 导入退出注册模块
from atexit import register

# 导入NoneBot框架相关模块
import nonebot
# 导入日志记录器
from nonebot.log import logger
# 导入OneBot v11适配器
from nonebot.adapters.onebot.v11 import Adapter

# 定义日志文件夹路径
log_path = Path('./Logs/')
# 如果日志文件夹不存在，则创建之
if not log_path.exists():
    log_path.mkdir()
# 添加日志处理器，按天轮转日志
logger.add((log_path / '{time}.log'), rotation='1 day')

# 初始化NoneBot框架
nonebot.init()

# 加载插件
nonebot.load_plugins('Plugins')

# 获取驱动器对象
driver = nonebot.get_driver()
# 注册适配器
driver.register_adapter(Adapter)


# 定义启动时运行的异步函数
@driver.on_startup
async def startup():
    # 导入网络相关脚本
    from Scripts import Network
    # 导入WebSocket服务管理器
    from Scripts.Servers import Websocket
    # 导入HTTP服务管理器
    from Scripts.Servers.Http import WebUi
    # 导入各种管理器
    from Scripts.Managers import environment_manager, lagrange_manager, version_manager, data_manager

    # 初始化拉格朗日管理器
    await lagrange_manager.init()
    # 初始化版本管理器
    await version_manager.init()
    # 如果有更新，则更新版本
    if version_manager.check_update():
        await version_manager.update_version()

    # 加载数据管理器
    data_manager.load()
    # 初始化环境管理器
    environment_manager.init()
    # 设置WebUI的HTTP服务器
    WebUi.setup_webui_http_server()
    # 设置WebSocket服务器
    Websocket.setup_websocket_server()

    # 发送机器人在线状态
    await Network.send_bot_status(True)


# 定义关闭时运行的异步函数
@driver.on_shutdown
async def shutdown():
    # 导入网络相关脚本
    from Scripts import Network
    # 导入数据管理器
    from Scripts.Managers import data_manager

    # 保存数据
    data_manager.save()

    # 发送机器人离线状态
    await Network.send_bot_status(False)


# 如果是主程序，则注册关闭处理函数，并运行NoneBot框架
if __name__ == '__main__':
    register(shutdown)
    nonebot.run()
