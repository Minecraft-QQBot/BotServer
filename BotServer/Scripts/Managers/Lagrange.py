# 导入系统平台信息模块
import platform
# 导入处理 tar 文件的模块
import tarfile
# 导入异步编程模块
import asyncio
# 从 asyncio 模块中导入 Task 类型定义
from asyncio import Task
# 从 asyncio.subprocess 模块中导入 Process 类型和 PIPE 常量，用于异步调用外部命令
from asyncio.subprocess import Process, PIPE
# 导入处理路径的模块
from pathlib import Path
# 导入处理 JSON 数据的模块
from json import load, dump

# 导入 nonebot 的日志模块
from nonebot.log import logger

# 导入自定义的配置模块和下载函数
from ..Config import config
from ..Network import download


# 定义 LagrangeManager 类，用于管理 Lagrange.OneBot 的安装、配置和运行
class LagrangeManager:
    # 类变量初始化，包括任务、进程和 Lagrange 路径
    task: Task = None
    process: Process = None
    lagrange_path: Path = None

    # 定义 Lagrange 软件的存储路径
    path: Path = Path('Lagrange')

    # 构造函数，初始化时自动查找已安装的 Lagrange.OneBot 路径
    def __init__(self):
        for path in self.path.rglob('Lagrange.OneBot*'):
            self.lagrange_path = path.absolute()

    # 异步方法，用于更新 Lagrange.OneBot 的配置文件
    async def update_config(self):
        # 检查配置文件模板是否存在，若不存在则报错并退出
        config_path = Path('Resources/Lagrange.json')
        if not config_path.exists():
            logger.error('找不到 Lagrange.Onebot 的配置文件模版！请尝试重新安装机器人。')
            exit(1)
        # 读取配置文件模板内容
        with config_path.open('r', encoding='Utf-8') as file:
            lagrange_config = load(file)
        # 写入新的配置文件，包括从自定义配置模块获取的端口和访问令牌
        config_path = (self.path / 'appsettings.json')
        lagrange_config['Implementations'][0]['Port'] = config.port
        lagrange_config['Implementations'][0]['AccessToken'] = config.onebot_access_token
        with config_path.open('w', encoding='Utf-8') as file:
            dump(lagrange_config, file)
            logger.success('Lagrange.Onebot 配置文件更新成功！')
            return True

    # 静态方法，用于解析当前系统的平台和架构
    @staticmethod
    def parse_platform():
        # 获取系统平台和机器架构
        system = platform.system()
        architecture = platform.machine()
        # 定义系统名称映射表
        system_mapping = {'Linux': 'linux', 'Darwin': 'osx', 'Windows': 'win'}
        # 根据不同系统平台，确定对应的架构名称
        if system == 'Windows':
            architecture = 'x64' if architecture == 'AMD64' else 'x86'
        elif system == 'Darwin':
            architecture = 'x64' if architecture == 'x86_64' else 'arm64'
        elif system == 'Linux':
            architecture = 'x64' if architecture == 'x86_64' else 'arm'
        return system_mapping[system], architecture

    # 异步方法，用于初始化 Lagrange.OneBot，如果已安装则自动启动
    async def init(self):
        if self.lagrange_path:
            logger.info('Lagrange.Onebot 已经安装，正在自动启动……')
            self.task = asyncio.create_task(self.run())

    # 异步方法，用于停止 Lagrange.OneBot 进程
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

    # 异步方法，用于运行 Lagrange.OneBot 进程，并输出日志
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

    # 异步方法，用于安装 Lagrange.OneBot
    async def install(self):
        # 检查是否已安装，已安装则不重复安装
        if self.lagrange_path:
            logger.warning('Lagrange.Onebot 已经安装，无需再次安装！')
            return True
        # 创建存储路径并设置权限
        if not self.path.exists():
            self.path.mkdir()
        self.path.chmod(0o755)
        # 解析系统平台和架构，并下载对应的安装包
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


# 实例化 LagrangeManager 类
lagrange_manager = LagrangeManager()
