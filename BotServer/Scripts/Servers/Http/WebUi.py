# 导入JSON处理和文件路径管理的库
from json import dumps
from pathlib import Path

# 导入FastAPI的静态文件管理
from fastapi.staticfiles import StaticFiles
# 导入NoneBot框架和日志记录器
from nonebot import get_driver, get_app
# 导入NoneBot的驱动接口和HTTP服务器设置
from nonebot.drivers import URL, Request, Response, ASGIMixin, HTTPServerSetup
# 导入环境管理和数据管理模块
from nonebot.log import logger

# 导入环境管理和数据管理模块，用于后续的任务环境配置与数据处理
from Scripts.Managers import environment_manager, data_manager
# 导入重启函数
from Scripts.Utils import restart


# 定义API处理函数
async def api(request: Request):
    # 验证请求的Token
    if request.headers.get('token') != data_manager.webui_token:
        return Response(403, content=dumps({'success': False}))
    # 处理POST请求，更新环境配置
    if request.method == 'POST':
        environment_manager.update(request.json)
        message = '机器人即将自动重启！' if restart() else '当前系统不支持自动重启，请手动重启机器人！'
        return Response(200, content=dumps({'success': True, 'message': message}))
    # 处理GET请求，返回环境配置
    response = {'success': True, 'data': environment_manager.environment}
    return Response(200, content=dumps(response))


# 定义Web页面处理函数
async def page(request: Request):
    page_path = Path('Resources/WebUi/Index.html')
    with page_path.open('r', encoding='Utf-8') as file:
        return Response(200, content=file.read())


# 定义WebUI的HTTP服务器设置函数
def setup_webui_http_server():
    # 检查驱动类型并设置静态文件目录和HTTP服务器
    if isinstance((driver := get_driver()), ASGIMixin):
        application = get_app()
        application.mount('/assets', StaticFiles(directory='Resources/WebUi/Assets'), name='static_assets')

        server = HTTPServerSetup(URL('/webui'), 'GET', 'page', page)
        driver.setup_http_server(server)
        server = HTTPServerSetup(URL('/webui/api'), 'GET', 'get_api', api)
        driver.setup_http_server(server)
        server = HTTPServerSetup(URL('/webui/api'), 'POST', 'post_api', api)
        driver.setup_http_server(server)
        logger.success('载入 WebUi 成功！请保管好下方的链接，以供使用。')
        color_logger = logger.opt(colors=True)
        color_logger.info(
            F'WebUi <yellow><b>http://{driver.config.host}:{driver.config.port}'
            F'/webui?token={data_manager.webui_token}</b></yellow>'
        )
        return True
    # 驱动不支持HTTP服务器，记录错误日志
    logger.error('当前驱动不支持 Http 服务器！载入 WebUi 失败，请检查驱动是否正确。')
