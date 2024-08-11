import asyncio

import nonebot
from nonebot.adapters.onebot.v11 import Adapter


nonebot.init()

nonebot.load_plugins('Plugins')

driver = nonebot.get_driver()
driver.register_adapter(Adapter)


@driver.on_startup
def startup():
    from Scripts.Servers import Websocket
    from Scripts.Servers.Http import WebUi
    from Scripts.Managers import Logger, environment_manager, data_manager, version_manager

    if version_manager.check_update():
        asyncio.run(version_manager.update_version())

    Logger.init()
    data_manager.load()
    environment_manager.init()
    Websocket.setup_websocket_server()
    WebUi.setup_webui_http_server()


@driver.on_shutdown
def shutdown():
    from Scripts.Managers import data_manager

    data_manager.save()


if __name__ == '__main__':
    nonebot.run()
