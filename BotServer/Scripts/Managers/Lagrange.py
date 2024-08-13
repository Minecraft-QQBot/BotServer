import platform
import tarfile
import asyncio
from pathlib import Path
from json import load, dump

from nonebot.log import logger

from ..Config import config
from ..Network import download


class LagrangeManager:
    task = None
    lagrange: list = None

    path: Path = Path('Lagrange')

    def __init__(self):
        self.lagrange = list(self.path.rglob('Lagrange.OneBot*'))

    def init(self):
        self.update_config()
        if self.lagrange:
            logger.info('检测到 Lagrange.Onebot 已经安装，正在启动……')

    def start(self):
        process = asyncio.create_subprocess_exec(self.lagrange[0])
        self.task = asyncio.create_task(process)

    def update_config(self):
        config_path = (self.path / 'appsettings.json')
        lagrange_config_path = Path('Resources/Lagrange.json')
        if not lagrange_config_path.exists():
            logger.error('Lagrange.Onebot 配置文件不存在，初始化配置文件失败！')
            return False
        with lagrange_config_path.open('r', encoding='Utf-8') as file:
            lagrange_config = load(file)
        lagrange_config['Implementations'][0]['Port'] = config.port
        lagrange_config['Implementations'][0]['AccessToken'] = config.onebot_access_token
        with config_path.open('w', encoding='Utf-8') as file:
            dump(lagrange_config, file)
            logger.success('Lagrange.Onebot 配置文件更新成功！')
            return True

    async def install(self):
        if self.lagrange:
            logger.warning('Lagrange.Onebot 已经安装，无需再次安装！')
            return True
        if not self.path.exists():
            self.path.mkdir()
        self.path.chmod(0o755)
        system, architecture = self.parse_platform()
        logger.info(F'检测到当前的系统架构为 {system} {architecture} 正在下载对应的安装包……')
        if response := await download(F'https://github.com/LagrangeDev/Lagrange.Core/releases/download/nightly/Lagrange.OneBot_{system}-{architecture}_net8.0_SelfContained.tar.gz'):
            logger.success(F'Lagrange.Onebot 下载成功！正在安装……')
            with tarfile.open(fileobj=response) as zip_file:
                for member in zip_file.getmembers():
                    if member.isfile():
                        with zip_file.extractfile(member) as file:
                            file_name = file.name.split('/')[-1]
                            with open((self.path / file_name), 'wb') as target_file:
                                target_file.write(file.read())
            logger.success('Lagrange.Onebot 安装成功！')
            self.lagrange.append(next(self.path.rglob('Lagrange.OneBot*')))
            return self.update_config()
        logger.error('Lagrange.Onebot 安装失败！')
        return False

    @staticmethod
    def parse_platform():
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
