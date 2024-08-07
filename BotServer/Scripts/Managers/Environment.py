from json import JSONDecodeError, loads, dumps
from pathlib import Path

from nonebot.log import logger


class EnvironmentManager:
    mapping: list = []
    environment: dict = {}

    file_path: Path = Path('.env')

    def init(self):
        if not self.file_path.exists():
            logger.error('没有找到配置文件！请重新下载后重试。')
            exit(1)
        self.load()

    def load(self):
        with self.file_path.open('r', encoding='Utf-8') as file:
            for line in file:
                line = line.strip()
                if line.startswith('#') or (not line):
                    self.mapping.append(line)
                    continue
                key, value = line.split('=')
                key, value = key.strip(), value.strip()
                try:
                    value = loads(value)
                except JSONDecodeError:
                    pass
                self.environment[key] = value
                self.mapping.append(key)
            logger.success('预加载配置文件完毕！文件已载入到内存中。')

    def update(self, new: dict):
        logger.info(F'正在更新配置 {new}')
        for key, value in new.items():
            self.environment[key] = value
        self.write()

    def write(self):
        logger.info('正在写入配置……')
        lines = []
        for line in self.mapping:
            if line.startswith('#') or (not line):
                lines.append(line)
                continue
            lines.append(F'{line}={dumps(self.environment[line])}')
        with self.file_path.open('w', encoding='Utf-8') as file:
            file.write('\n'.join(lines))
        logger.success('写入配置成功！手动重启机器人后修改才会生效。')


environment_manager = EnvironmentManager()
