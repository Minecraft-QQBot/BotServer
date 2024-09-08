import sys
from pathlib import Path
from tempfile import gettempdir
from zipfile import ZipFile

from nonebot.log import logger


class ResourcesManager:
    path: Path = (Path(gettempdir()) / 'BotResources')

    def init(self):
        logger.debug('正在初始化资源管理器……')
        if not self.path.exists():
            logger.info('未找到资源文件，正在提取……')
            self.path.mkdir()
            self.extract()
        logger.success('资源管理器初始化完成！')

    def remove(self):
        self.path.rmdir()

    def read_file(self, file_path: str):
        file_path = (self.path / file_path)
        return file_path.read_text('Utf-8')

    def extract(self):
        with ZipFile(sys.argv[0], 'r') as zip_file:
            for file in zip_file.namelist():
                if file.startswith('Resources/') and (file != 'Resources/'):
                    file_path = file[10:]
                    print(file_path)
                    target_path = (self.path / file_path)
                    if '.' in file_path:
                        with target_path.open('wb') as target_file:
                            target_file.write(zip_file.read(file))
                        continue
                    target_path.mkdir()


resources_manager = ResourcesManager()
