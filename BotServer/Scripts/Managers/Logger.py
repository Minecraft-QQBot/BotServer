from pathlib import Path

from nonebot.log import logger


def init():
    log_path = Path('./Logs/')
    if not log_path.exists():
        log_path.mkdir()
    logger.add((log_path / '{time}.log'), ratition='1 day')
