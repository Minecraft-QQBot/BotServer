from json import dumps

from nonebot import get_driver
from nonebot.drivers import URL, Request, Response, ASGIMixin, HTTPServerSetup
from nonebot.log import logger

from Scripts.Config import config
from Scripts.Managers import server_manager, data_manager


async def broadcast(request: Request):
    if request.headers.get('token') != config.api_token:
        return Response(403, content=dumps({'success': False}))
    if message := request.json.get('message'):
        if server_flag := request.json.get('server'):
            if server := server_manager.get_server(server_flag):
                await server.broadcast(message)
                return Response(200, content=dumps({'success': True}))
            return Response(200, content=dumps({'success': False, 'message': '服务器不存在！'}))
        await server_manager.broadcast(message)
        return Response(200, content=dumps({'success': True}))
    return Response(200, content=dumps({'success': False, 'message': '缺少必要的消息参数！'}))


async def get_player_list(request: Request):
    if request.headers.get('token') != config.api_token:
        return Response(403, content=dumps({'success': False}))
    if server_flag := request.url.query.get('server'):
        if server := server_manager.get_server(server_flag):
            return Response(200, content=dumps({'success': True, 'data': await server.send_player_list()}))
        return Response(200, content=dumps({'success': False, 'message': '服务器不存在！'}))
    return Response(200, content=dumps({'success': True, 'data': await data_manager.get_player_list()}))


async def get_server_occupation(request: Request):
    if request.headers.get('token') != config.api_token:
        return Response(403, content=dumps({'success': False}))
    if server_flag := request.url.query.get('server'):
        if server := server_manager.get_server(server_flag):
            return Response(200, content=dumps({'success': True, 'data': await server.send_server_occupation()}))
        return Response(200, content=dumps({'success': False, 'message': '服务器不存在！'}))
    return Response(200, content=dumps({'success': True, 'data': await server_manager.get_server_occupation()}))


async def execute_command(request: Request):
    if request.headers.get('token') != config.api_token:
        return Response(403, content=dumps({'success': False}))
    if command := request.json.get('command'):
        if server_flag := request.json.get('server'):
            if server := server_manager.get_server(server_flag):
                return Response(200, content=dumps({'success': True, 'data': await server.send_command(command)}))
            return Response(200, content=dumps({'success': False, 'message': '服务器不存在！'}))
        return Response(200, content=dumps({'success': True, 'data': await server_manager.execute(command)}))
    return Response(200, content=dumps({'success': False, 'message': '缺少必要的命令参数！'}))


async def execute_mcdr_command(request: Request):
    if request.headers.get('token') != config.api_token:
        return Response(403, content=dumps({'success': False}))
    if command := request.json.get('command'):
        if server_flag := request.json.get('server'):
            if server := server_manager.get_server(server_flag):
                if server.type in ('McdReforged', 'FakePlayer'):
                    result = await server.send_mcdr_command(command)
                    return Response(200, content=dumps({'success': True, 'data': result}))
                return Response(200, content=dumps({'success': False, 'message': '此服务器不支持 MCDR 命令！'}))
            return Response(200, content=dumps({'success': False, 'message': '服务器不存在！'}))
        return Response(200, content=dumps({'success': True, 'data': await server_manager.execute_mcdr(command)}))
    return Response(200, content=dumps({'success': False, 'message': '缺少必要的命令参数！'}))


def setup_api_http_server():
    if not config.api_enabled:
        return None
    if isinstance((driver := get_driver()), ASGIMixin):
        api_servers = (
            HTTPServerSetup(URL('/api/get_player_list'), 'GET', 'api.player_list', get_player_list),
            HTTPServerSetup(URL('/api/get_server_occupation'), 'GET', 'api.server_occupation', get_server_occupation),
            HTTPServerSetup(URL('/api/broadcast'), 'POST', 'api.broadcast', broadcast),
            HTTPServerSetup(URL('/api/execute_command'), 'POST', 'api.command', execute_command),
            HTTPServerSetup(URL('/api/execute_mcdr_command'), 'POST', 'api.mcdr_command', execute_mcdr_command),
        )
        for api_server in api_servers:
            driver.setup_http_server(api_server)
        logger.success('载入 Api 服务器成功！')
        return True
    logger.error('当前驱动不支持 Http 服务器！载入 Api 服务器失败！请检查驱动是否正确。')
