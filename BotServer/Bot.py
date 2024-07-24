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
    from Scripts.ServerWatcher import server_watcher
    from Scripts.Managers import server_manager, data_manager

    data_manager.load()
    server_manager.init()
    server_watcher.start()
    Websocket.setup_websocket_server()


@driver.on_shutdown
def shutdown():
    from Scripts.Managers import server_manager, data_manager
    
    data_manager.save()
    task = asyncio.create_task(server_manager.unload())
    asyncio.run(task)


if __name__ == '__main__':
    nonebot.run()
