import asyncio

import nonebot
from nonebot.adapters.onebot.v11 import Adapter

nonebot.init()

nonebot.load_plugins('Plugins')

driver = nonebot.get_driver()
driver.register_adapter(Adapter)


@driver.on_startup
def startup():
    from Scripts.ServerWatcher import server_watcher
    from Scripts.Servers import Websocket
    from Scripts.Managers import Logger, environment_manager, data_manager
    from Scripts.Servers.Http import WebUi

    Logger.init()
    data_manager.load()
    server_watcher.start()
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
