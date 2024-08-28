from json import dumps
from pathlib import Path

from nonebot import get_driver
from nonebot.drivers import URL, Request, Response, ASGIMixin, HTTPServerSetup
from nonebot.log import logger

from Scripts.Config import config
from Scripts.Managers import server_manager, data_manager


async def get_player_list(request: Request):
    if request.headers.get('token') != config.api_token:
        return Response(403, content=dumps({'success': False}))
    if server_flag := request.url.query.get('server'):
        if server := server_manager.get_server(server_flag):
            return Response(200, content=dumps({'success': True, 'players': await server.send_player_list()}))
        return Response(200, content=dumps({'success': False, 'message': '服务器不存在！'}))
    players = {
        server.name: await server.send_player_list()
        for server in server_manager.servers.values() if server.status
    }
    return Response(200, content=dumps({'success': True, 'players': players}))


def setup_api_http_server():
    if not config.api_token:
        return None
    if isinstance((driver := get_driver()), ASGIMixin):
        api_servers = (
            HTTPServerSetup(URL('/api/player_list'), 'GET', 'api.player_list', get_player_list),
        )
        for api_server in api_servers:
            driver.setup_http_server(api_server)
        logger.success('载入 Api 服务器成功！请保管好下方的链接，以供使用。')
        return True
    logger.error('当前驱动不支持 Http 服务器！载入 Api 服务器失败！请检查驱动是否正确。')
