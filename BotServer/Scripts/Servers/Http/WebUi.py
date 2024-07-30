from json import dumps
from pathlib import Path

from nonebot import get_driver, get_app
from nonebot.drivers import URL, Request, Response, ASGIMixin, HTTPServerSetup
from nonebot.log import logger

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from Scripts.Managers import environment_manager, data_manager


async def api(request: Request):
    if request.headers.get('token') != data_manager.webui_token:
        return Response(403, content=dumps({'success': False}))
    if request.method == 'POST':
        environment_manager.update(request.json)
        return Response(200, content=dumps({'success': True}))
    response = {'success': True, 'data': environment_manager.environment}
    return Response(200, content=dumps(response))


async def page(request: Request):
    page_path = Path('Resources/WebUi/index.html')
    with page_path.open('r', encoding='Utf-8') as file:
        return Response(200, content=file.read())


def setup_webui_http_server():
    application: FastAPI = get_app()
    application.mount('/assets', StaticFiles(directory='Resources/WebUi/Assets'), name='static_assets')
    if isinstance((driver := get_driver()), ASGIMixin):
        server = HTTPServerSetup(URL('/webui'), 'GET', 'page', page)
        driver.setup_http_server(server)
        server = HTTPServerSetup(URL('/webui/api'), 'GET', 'get_api', api)
        driver.setup_http_server(server)
        server = HTTPServerSetup(URL('/webui/api'), 'POST', 'post_api', api)
        driver.setup_http_server(server)
        logger.success('载入基础 WebUi 成功！')
        return True
    logger.error('当前驱动不支持 Http 服务器！载入 WebUi 失败，请检查驱动是否正确。')
    exit(1)
