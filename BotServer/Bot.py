from Scripts.Managers import server_manager, data_manager

import nonebot
from nonebot.adapters.onebot.v11 import Adapter

nonebot.init()

nonebot.load_plugins('Plugins')

driver = nonebot.get_driver()
driver.register_adapter(Adapter)


@driver.on_startup
def startup():
    from Scripts import HttpServer

    data_manager.load()
    server_manager.init()
    HttpServer.setup_http_server()


@driver.on_shutdown
def shutdown():
    data_manager.save()
    server_manager.unload()


if __name__ == '__main__':
    nonebot.run()
