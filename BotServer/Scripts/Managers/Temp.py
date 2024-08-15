import tempfile
from pathlib import Path
from json import dump, load

from nonebot.log import logger


class TempManager:
    file_path: Path = None

    player_uuid: list = []
    chart_font_path: str = None

    def __init__(self):
        directory = Path(tempfile.gettempdir())
        self.file_path = (directory / 'QQBot.tmp')

    def load(self):
        if self.file_path.exists():
            with self.file_path.open('r', encoding='Utf-8') as file:
                temp_data = load(file)
                self.file_path = temp_data['font']
                self.player_uuid = temp_data['player']
                logger.success('临时文件加载成功！')
        logger.info('临时文件不存在，正在创建！')
        self.save()

    def save(self):
        with self.file_path.open('w', encoding='Utf-8') as file:
            dump({'font': self.chart_font_path, 'player': self.player_uuid}, file)
            logger.success('临时文件保存成功！')


temp_manager = TempManager()
