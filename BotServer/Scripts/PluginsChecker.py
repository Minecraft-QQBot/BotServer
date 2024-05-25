from Config import config

from os import listdir, rename

from nonebot.log import logger


def check(path: str):
    logger.info('正在检查插件……')
    for name in listdir(path):
        if name.startswith('__'):
            continue
        file_path = (path + name)
        name = name.lower().rstrip('.disabled').rstrip('.py')
        if file_path.endswith('.disabled') and (name not in config.command_disabled):
            logger.info(F'已重新启用指令 {name} ！')
            rename(file_path, file_path.rstrip('.disabled'))
        elif file_path.endswith('.py') and (name in config.command_disabled):
            logger.info(F'已重禁用指令 {name} 。')
            rename(file_path, (file_path + '.disabled'))
    logger.success('检查插件完成！')
