import platform
from zipfile import ZipFile
from pathlib import Path

from nonebot.log import logger

from ..Network import download


class LagrangeManager:
    status: str = None
    lagrange_path: Path = Path('Lagrange')

    def __init__(self):
        if self.lagrange_path.exists() and self.lagrange_path.rglob('Lagrange.OneBot*'):
            self.status = 'installed'

    def parse_platform(self):
        system = platform.system()
        architecture = platform.machine()
        system_mapping = {'Linux': 'linux', 'Darwin': 'osx', 'Windows': 'win'}
        if system == 'Windows':
            architecture = 'x64' if architecture == 'AMD64' else 'x86'
        elif system == 'Darwin':
            architecture = 'x64' if architecture == 'x86_64' else 'arm64'
        elif system == 'Linux':
            architecture = 'x64' if architecture == 'x86_64' else 'arm'
        return system_mapping[system], architecture

    async def install(self):
        if not self.lagrange_path.exists():
            self.lagrange_path.mkdir()
        system, architecture = self.parse_platform()
        logger.info(F'检测到当前的系统架构为 {system}-{architecture} 正在下载对应的安装包……')
        if response := await download(
                F'https://github.com/LagrangeDev/Lagrange.Core/releases/download/nightly/Lagrange.OneBot_{system}-{architecture}_net8.0_SelfContained.tar.gz'):
            logger.success(F'Lagrange.Onebot 下载成功！正在安装……')
            with ZipFile(response) as zip_file:
                for file in zip_file.namelist():
                    zip_file.extract(file, self.lagrange_path)


if __name__ == '__main__':
    lagrange_manager = LagrangeManager()
