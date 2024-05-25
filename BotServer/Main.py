from Config import config
from Scripts import PluginsChecker, HttpServer

from pathlib import Path

import nonebot
from nonebot.adapters.onebot.v11 import Adapter

nonebot.init()

PluginsChecker.check('./Plugins/Commands/')
nonebot.load_plugins('./Plugins/Commands/')
nonebot.load_plugin(Path('./Plugins/SyncMessage.py'))

driver = nonebot.get_driver()
driver.register_adapter(Adapter)


@driver.on_startup
def startup():
    HttpServer.setup_http_server()


@driver.on_shutdown
def shutdown():
    config.save()


if __name__ == '__main__':
    nonebot.run()
