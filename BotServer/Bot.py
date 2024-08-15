import asyncio
from atexit import register

import nonebot
from nonebot.adapters.onebot.v11 import Adapter

from Scripts.Network import send_bot_status

nonebot.init()

nonebot.load_plugins('Plugins')

driver = nonebot.get_driver()
driver.register_adapter(Adapter)


@driver.on_startup
def startup():
    from Scripts.Servers import Websocket
    from Scripts.Servers.Http import WebUi
    from Scripts.Managers import Logger, environment_manager, data_manager, version_manager, lagrange_manager

    lagrange_manager.init()
    version_manager.init()
    if version_manager.check_update():
        asyncio.run(version_manager.update_version())

    Logger.init()
    data_manager.load()
    environment_manager.init()
    Websocket.setup_websocket_server()
    WebUi.setup_webui_http_server()
    send_bot_status(True)



@driver.on_shutdown
def shutdown():
    from Scripts.Managers import data_manager

    data_manager.save()
    send_bot_status(False)


if __name__ == '__main__':
    register(shutdown)
    nonebot.run()
