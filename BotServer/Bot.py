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
    from Scripts.Managers import data_manager
    from Scripts.ServerWatcher import server_watcher

    data_manager.load()
    server_watcher.start()
    Websocket.setup_websocket_server()


@driver.on_shutdown
def shutdown():
    from Scripts.Managers import server_manager, data_manager
    
    data_manager.save()
    asyncio.run(server_manager.unload())


if __name__ == '__main__':
    nonebot.run()
