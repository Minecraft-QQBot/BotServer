# 导入操作系统相关功能，用于创建目录和检查路径
from os import mkdir, path
# 导入压缩文件处理功能
from zipfile import ZipFile

# 导入日志记录功能
from nonebot.log import logger

# 导入网络操作相关功能，包括下载文件和发送请求
from ..Network import download, request


# 定义版本管理类
class VersionManager:
    # 当前版本号
    version: str = 'v2.0.4'
    # 最新版本号，初始为None
    latest_version: str = None

    # 检查是否有更新
    # 无需参数
    # 返回是否有新版本可供更新
    def check_update(self):
        # 如果latest_version为None，表示尚未检查更新
        if self.latest_version is None:
            return False
        # 返回当前版本与最新版本是否不同
        return self.latest_version != self.version

    # 初始化，获取最新版本信息
    # 无需参数
    # 返回值为None或引发异常
    async def init(self):
        # 发送请求获取最新版本信息
        if response := await request('http://api.qqbot.bugjump.xyz/version'):
            # 提取并存储最新版本号
            self.latest_version = response.get('version')
            return None
        # 请求失败，记录警告日志
        logger.warning('尝试获取新版本时出错！')

    # 执行更新操作
    # 无需参数
    # 返回值为None或引发异常
    async def update_version(self):
        # 记录更新开始的日志
        logger.info(F'更新版本到 {self.latest_version}……')
        # 下载最新版本的压缩包
        if response := await download(
                F'https://github.com/Minecraft-QQBot/BotServer/releases/download/v{self.latest_version}/BotServer-v{self.latest_version}.zip'):
            # 解压缩并替换旧文件
            with ZipFile(response) as zip_file:
                for file in zip_file.namelist():
                    # 忽略配置文件和特定目录
                    if file.startswith('BotServer/') and ('.env' not in file):
                        file_path = file[10:]
                        # 如果是文件，则写入新内容
                        if '.' in file_path:
                            with open(file_path, 'wb') as target_file:
                                target_file.write(zip_file.read(file))
                            continue
                        # 如果是目录且不存在，则创建
                        if not path.exists(file_path) and file_path:
                            mkdir(file_path)
            # 更新成功，记录成功日志并提示重启机器人
            logger.success(F'更新版本到 {self.latest_version} 成功！请重启机器人。')
            return None
        # 更新失败，记录警告日志
        logger.warning(F'更新版本到 {self.latest_version} 失败，请检查网络稍后再试。')


# 创建版本管理器实例
version_manager = VersionManager()
