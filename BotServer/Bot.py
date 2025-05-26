from atexit import register
from pathlib import Path

import nonebot
from nonebot.adapters.onebot.v11 import Adapter
from nonebot.log import logger

nonebot.init()

nonebot.load_plugins('Plugins')

driver = nonebot.get_driver()
driver.register_adapter(Adapter)


def main():
    log_path = Path('./Logs/')
    if not log_path.exists():
        log_path.mkdir()
    logger.add((log_path / '{time}.log'), rotation='1 day')

    register(shutdown)
    nonebot.run()


@driver.on_startup
async def startup():
    from Scripts import Network
    from Scripts.Servers import Websocket, Http
    from Scripts.Managers import (
        version_manager, data_manager,
        environment_manager, lagrange_manager, resources_manager
    )

    resources_manager.init()

    await version_manager.init()
    await lagrange_manager.init()
    # if version_manager.check_update():
    #     await version_manager.update_version()

    data_manager.load()
    environment_manager.init()
    Websocket.setup_websocket_server()
    Http.setup_api_http_server()
    Http.setup_webui_http_server()

    await Network.send_bot_status(True)


@driver.on_shutdown
async def shutdown():
    from Scripts import Network
    from Scripts.Managers import data_manager

    data_manager.save()

    await Network.send_bot_status(False)


if __name__ == '__main__':
    main()
