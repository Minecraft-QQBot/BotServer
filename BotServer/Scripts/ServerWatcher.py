from .Config import config

from time import sleep
from psutil import Process
from threading import Thread

from nonebot.log import logger


class ServerWatcher(Thread):
    cpus: dict[str, list] = {}
    rams: dict[str, list] = {}
    processes: dict[str, Process] = {}

    def __init__(self):
        Thread.__init__(self, name='ServerWatcher', daemon=True)

    def run(self):
        logger.info('服务器监视线程启动。')
        while True:
            logger.debug('定时获取更新服务器信息。')
            data = self.get_data()
            for name, (cpu, ram) in data.items():
                if len(self.cpus[name]) > config.server_watcher_max_cache:
                    self.cpus[name].pop(0)
                    self.rams[name].pop(0)
                self.cpus[name].append(cpu)
                self.rams[name].append(ram)
            sleep(config.server_watcher_update_interval)

    def get_data(self, server_name: str = None):
        if not server_name:
            result = {}
            for name, process in self.processes.items():
                result[name] = (process.cpu_percent(), round(process.memory_percent(), 1))
            return result
        if process := self.processes.get(server_name):
            return process.cpu_percent(), round(process.memory_percent(), 1)
        return None

    def append_server(self, name: str, pid: int):
        self.cpus[name] = []
        self.rams[name] = []
        try:
            process = Process(pid)
            process.cpu_percent(interval=0.1)
        except Exception:
            logger.warning(F'设置监视服务器 [{name}] PID 为 {pid} 失败！')
            return None
        self.processes[name] = process
        logger.success(F'设置监视服务器 [{name}] PID 为 {pid} 成功！')

    def remove_server(self, name: str):
        self.cpus.pop(name, None)
        self.rams.pop(name, None)
        self.processes.pop(name, None)
        logger.success(F'移除监视服务器 [{name}] 成功！')


server_watcher = ServerWatcher()
