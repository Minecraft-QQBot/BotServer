from io import BytesIO
from zipfile import ZipFile

from httpx import AsyncClient
from nonebot.log import logger

__version__ = '2.0.2'


async def check_update():
    latest_version = await get_latest_version()
    if __version__ != latest_version:
        color_logger = logger.opt(colors=True)
        color_logger.info(F'<blue><b>发现新版本 {latest_version}</b></blue>。')
        return latest_version
    return False


async def get_latest_version():
    async with AsyncClient() as client:
        response = await client.get('https://qqbot.ylmty.cc/version.json')
    if response.status_code == 200:
        return response.json()[0]


async def update_version(version: str):
    logger.info(F'更新版本到 {version}...')
    if version_bytes := await download_version(version):
        with ZipFile(version_bytes) as zip_file:
            for file in zip_file.namelist():
                if file.startswith('BotServer/') and ('.env' not in file):
                    zip_file.extract(file, path='./')
        logger.success(F'更新版本到 {version} 成功！请重启机器人。')
        exit()
    logger.warning(F'更新版本到 {version} 失败，请检查网络稍后再试。')


async def download_version(version: str):
    version_bytes = BytesIO()
    url = F'https://github.com/Minecraft-QQBot/BotServer/releases/download/v{version}/BotServer-v{version}.zip'
    async with AsyncClient() as client:
        async with client.stream('GET', F'https://mirror.ghproxy.com/{url}') as stream:
            if stream.status_code != 200:
                return False
            async for chunk in stream.aiter_bytes():
                version_bytes.write(chunk)
            version_bytes.seek(0)
            return version_bytes
