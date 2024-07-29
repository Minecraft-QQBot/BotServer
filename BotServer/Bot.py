import asyncio

import nonebot
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import Adapter


from Scripts.Managers import environment_manager


nonebot.init()

nonebot.load_plugins('Plugins')

driver = nonebot.get_driver()
driver.register_adapter(Adapter)


@driver.on_startup
def startup():
    from Scripts.Servers import Websocket
    from Scripts.Managers import data_manager

    data_manager.load()
    environment_manager.init()
    Websocket.setup_websocket_server()
    webui_url = F'http://127.0.0.1:{driver.config.host}/webui?token={data_manager.webui_token}'
    logger.info(F'WebUi 网址为 <yellow><b>{webui_url}</b></yellow> ，请保护好否则可能遭受攻击。')


@driver.on_shutdown
def shutdown():
    from Scripts.Managers import server_manager, data_manager
    
    data_manager.save()
    asyncio.run(server_manager.unload())


if __name__ == '__main__':
    nonebot.run()
