import sys
from pathlib import Path
from zipfile import ZipFile

from nonebot.log import logger


class ResourcesManager:
    path: Path = Path('.Cache/Resources')

    def init(self):
        resources_path = Path('Resources')
        if resources_path.exists():
            self.path = resources_path
            logger.debug('检测到从源码运行，无需提取资源文件。')
            return None
        logger.debug('正在初始化资源管理器……')
        if not self.path.exists():
            logger.info('未找到资源文件，正在提取……')
            self.path.mkdir(parents=True)
            self.extract()
        logger.success('资源管理器初始化完成！')

    def remove(self):
        for child in self.path.rglob('*'):
            child.unlink()
        self.path.unlink()

    def read_file(self, file_path: str):
        file_path = (self.path / file_path)
        return file_path.read_text('Utf-8')

    def extract(self):
        cache_path = self.path.parent
        with ZipFile(sys.argv[0], 'r') as zip_file:
            for file in zip_file.namelist():
                if file.startswith('Resources/'):
                    zip_file.extract(file, cache_path)
                    continue


resources_manager = ResourcesManager()
