from Scripts import HttpServer
from Scripts.Managers import server_manager, data_manager

from pathlib import Path

import nonebot
from nonebot.adapters.onebot.v11 import Adapter

nonebot.init()

nonebot.load_plugins('./Plugins/Commands/')
nonebot.load_plugin(Path('./Plugins/SyncMessage.py'))

driver = nonebot.get_driver()
driver.register_adapter(Adapter)


@driver.on_startup
def startup():
    data_manager.load()
    server_manager.init()
    HttpServer.setup_http_server()


@driver.on_shutdown
def shutdown():
    data_manager.save()
    server_manager.unload()


if __name__ == '__main__':
    nonebot.run()
