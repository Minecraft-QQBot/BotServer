from io import BytesIO
from zipfile import ZipFile
from os import mkdir, path

from httpx import AsyncClient, Client
from nonebot.log import logger

__version__ = '2.0.2'


class VersionManager:
    latest_version: str = None

    def __init__(self):
        with Client() as client:
            response = client.get('https://qqbot.ylmty.cc/Version.json')
        if response.status_code == 200:
            self.latest_version = response.json()[0]['version']
        logger.warning('尝试获取新版本时出错！')

    def check_update(self):
        if self.latest_version is None:
            return False
        return self.latest_version != __version__

    async def update_version(self):
        logger.info(F'更新版本到 {self.latest_version}...')
        if version_bytes := await self.download_version():
            with ZipFile(version_bytes) as zip_file:
                for file in zip_file.namelist():
                    if file.startswith('BotServer/') and ('.env' not in file):
                        file_path = file[10:]
                        if '.' in file_path:
                            with open(file_path, 'wb') as target_file:
                                target_file.write(zip_file.read(file))
                            continue
                        if not path.exists(file_path) and file_path:
                            mkdir(file_path)
            logger.success(F'更新版本到 {self.latest_version} 成功！请重启机器人。')
            exit()
        logger.warning(F'更新版本到 {self.latest_version} 失败，请检查网络稍后再试。')

    async def download_version(self):
        version_bytes = BytesIO()
        url = (
            F'https://github.com/Minecraft-QQBot/BotServer/releases/'
            F'download/v{self.latest_version}/BotServer-v{self.latest_version}.zip'
        )
        async with AsyncClient() as client:
            async with client.stream('GET', 'https://mirror.ghproxy.com/' + url) as stream:
                if stream.status_code != 200:
                    return False
                async for chunk in stream.aiter_bytes():
                    version_bytes.write(chunk)
                version_bytes.seek(0)
                return version_bytes


version_manager = VersionManager()
