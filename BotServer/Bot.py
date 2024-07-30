import asyncio

from nonebot import init as nb_init
import nonebot
from nonebot import get_app
from nonebot.adapters.onebot.v11 import Adapter
from fastapi.middleware.cors import CORSMiddleware


# 初始化nb
nb_init()
nonebot.load_plugins('Plugins')

# 获取 FastAPI 应用实例
application = get_app()

# 允许跨域请求
application.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

driver = nonebot.get_driver()
driver.register_adapter(Adapter)


@driver.on_startup
def startup():
    from Scripts.Servers import Websocket
    from Scripts.Managers import environment_manager, data_manager
    from Scripts.Servers.Http import WebUi

    data_manager.load()
    environment_manager.init()
    WebUi.setup_webui_http_server()
    Websocket.setup_websocket_server()


@driver.on_shutdown
def shutdown():
    from Scripts.Managers import server_manager, data_manager

    data_manager.save()
    asyncio.run(server_manager.unload())


if __name__ == '__main__':
    nonebot.run()
