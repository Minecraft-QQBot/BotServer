from atexit import register

import nonebot
from nonebot.adapters.onebot.v11 import Adapter


nonebot.init()

nonebot.load_plugins('Plugins')

driver = nonebot.get_driver()
driver.register_adapter(Adapter)


@driver.on_startup
async def startup():
    from Scripts import Network
    from Scripts.Servers import Websocket
    from Scripts.Servers.Http import WebUi
    from Scripts.Managers import (
        Logger, environment_manager, lagrange_manager,
        version_manager, data_manager, temp_manager
    )

    await lagrange_manager.init()
    await version_manager.init()
    if version_manager.check_update():
        await version_manager.update_version()

    Logger.init()
    data_manager.load()
    temp_manager.load()
    environment_manager.init()
    WebUi.setup_webui_http_server()
    Websocket.setup_websocket_server()

    await Network.send_bot_status(True)


@driver.on_shutdown
async def shutdown():
    from Scripts import Network
    from Scripts.Managers import data_manager, temp_manager

    data_manager.save()
    temp_manager.save()

    await Network.send_bot_status(False)


if __name__ == '__main__':
    register(shutdown)
    nonebot.run()
