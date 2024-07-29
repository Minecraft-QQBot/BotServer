from pathlib import Path
from nonebot import get_driver
from json import dumps, loads
from Scripts.Managers import environment_manager, data_manager
from nonebot.log import logger
from nonebot.drivers import URL, Request, Response, ASGIMixin, HTTPServerSetup

contents: dict = None


async def api(request: Request):
    if request.headers.get('token') != data_manager.webui_token:
        return Response(403, content=dumps({'success': False}))
    if request.method == 'POST':
        environment_manager.update(request.json)
        return Response(200, content=dumps({'success': True}))
    response = {'success': True, 'data': environment_manager.environment}
    return Response(200, content=dumps(response))


async def static_handler(request: Request):
    path = request.url.path[-1].upper()
    if path in contents:
        if '.' not in path:
            return Response(200, content=contents['Index.html'])
        return Response(200, content=contents[path])
    return Response(404)


def read_page():
    page_contents = {}
    webui_path = Path('./WebUi/')
    file_names = ('Index.html', 'Index.css', 'Index.js', 'Vite.svg')
    for file_name in file_names:
        file_path = (webui_path / file_name)
        if not file_path.exists():
            logger.error('WebUi 文件缺失！请重新下载安装后重试。')
            exit(1)
        with file_path.open('r', encoding='Utf-8') as file:
            page_contents[file_name.upper()] = file.read()
    return page_contents


def setup_static_server(driver: ASGIMixin):
    for url in ('/webui/assets/Vite.svg', '/webui/assets/Index.js', '/webui/assets/Index.css', '/webui'):
        server = HTTPServerSetup(URL(url), 'GET', url, static_handler)
        driver.setup_http_server(server)


def setup_webui_http_server():
    global contents
    contents = read_page()
    if isinstance((driver := get_driver()), ASGIMixin):
        setup_static_server(driver)
        server = HTTPServerSetup(URL('/webui/api'), 'GET', 'get_api', api)
        driver.setup_http_server(server)
        server = HTTPServerSetup(URL('/webui/api'), 'POST', 'post_api', api)
        driver.setup_http_server(server)
        logger.success('载入基础 WebUi 成功！')
        return True
    logger.error('当前驱动不支持 Http 服务器！载入 WebUi 失败，请检查驱动是否正确。')
    exit(1)
