import platform
import tarfile
from json import loads, dump
from pathlib import Path

import asyncio
from asyncio import Task
from asyncio.subprocess import Process, PIPE

from nonebot.log import logger

from ..Config import config
from ..Network import download
from .Resources import resources_manager


class LagrangeManager:
    task: Task = None
    process: Process = None
    lagrange_path: Path = None

    path: Path = Path('Lagrange')

    def __init__(self):
        for path in self.path.rglob('Lagrange.OneBot*'):
            self.lagrange_path = path.absolute()

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

    async def update_config(self):
        config_path = (self.path / 'appsettings.json')
        lagrange_config = loads(resources_manager.read_file('Lagrange.json'))
        lagrange_config['Implementations'][0]['Port'] = config.port
        lagrange_config['Implementations'][0]['AccessToken'] = config.onebot_access_token
        with config_path.open('w', encoding='Utf-8') as file:
            dump(lagrange_config, file)
            logger.success('Lagrange.Onebot 配置文件更新成功！')
            return True

    async def init(self):
        if self.lagrange_path:
            logger.info('Lagrange.Onebot 已经安装，正在自动启动……')
            self.task = asyncio.create_task(self.run())

    async def stop(self):
        async def checker(process: Process):
            await asyncio.sleep(10)
            if process.returncode is None:
                process.kill()

        if self.process:
            self.process.terminate()
            checker_task = asyncio.create_task(checker(self.process))
            await self.process.wait()
            checker_task.cancel()
            self.task.cancel()
            self.process = None

    async def run(self):
        await self.update_config()
        self.process = await asyncio.create_subprocess_exec(str(self.lagrange_path), stdout=PIPE, cwd=self.path)
        logger.success('Lagrange.Onebot 启动成功！请扫描目录下的图片或下面的二维码登录。')
        async for line in self.process.stdout:
            line = line.decode('Utf-8').strip()
            if line.startswith('█') or line.startswith('▀'):
                logger.info(line)
                continue
            elif '[FATAL]' in line:
                logger.error(line)
            elif '[WARNING]' in line:
                logger.warning(line)
            logger.debug('[Lagrange] ' + line)

    async def install(self):
        if self.lagrange_path:
            logger.warning('Lagrange.Onebot 已经安装，无需再次安装！')
            return True
        if not self.path.exists():
            self.path.mkdir()
        self.path.chmod(0o755)
        system, architecture = self.parse_platform()
        logger.info(F'检测到当前的系统架构为 {system} {architecture} 正在下载对应的安装包……')
        if response := await download(
                F'https://github.com/LagrangeDev/Lagrange.Core/releases/download/nightly/Lagrange.OneBot_{system}-{architecture}_net8.0_SelfContained.tar.gz'):
            logger.success(F'Lagrange.Onebot 下载成功！正在安装……')
            with tarfile.open(fileobj=response) as zip_file:
                for member in zip_file.getmembers():
                    if member.isfile():
                        with zip_file.extractfile(member) as file:
                            file_name = file.name.split('/')[-1]
                            with open((self.path / file_name), 'wb') as target_file:
                                target_file.write(file.read())
            logger.success('Lagrange.Onebot 安装成功！')
            self.lagrange_path = next(self.path.rglob('Lagrange.OneBot*'))
            self.lagrange_path.chmod(0o755)
            return self.update_config()
        logger.error('Lagrange.Onebot 安装失败！')
        return False


lagrange_manager = LagrangeManager()
