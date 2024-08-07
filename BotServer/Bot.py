import asyncio

import nonebot
from nonebot.adapters.onebot.v11 import Adapter

from Scripts import Version

nonebot.init()

nonebot.load_plugins('Plugins')

driver = nonebot.get_driver()
driver.register_adapter(Adapter)


@driver.on_startup
def startup():
    from Scripts.Servers import Websocket
    from Scripts.Managers import Logger, environment_manager, data_manager
    from Scripts.Servers.Http import WebUi

    if version := asyncio.run(Version.check_update()):
        Version.update_version(version)

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
