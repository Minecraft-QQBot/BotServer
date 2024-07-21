from Scripts.Utils import turn_message, rule
from Scripts.Managers import server_manager
from Scripts.ServerWatcher import server_watcher

from io import BytesIO
from matplotlib import pyplot
from matplotlib.font_manager import findSystemFonts, FontProperties

from nonebot import on_command
from nonebot.log import logger
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment, Message


font = None
matcher = on_command('server status', force_whitespace=True, block=True, priority=5, rule=rule)


@matcher.handle()
async def handle_group(event: GroupMessageEvent, args: Message = CommandArg()):
    global font
    if not font:
        font = find_font()
    if args := args.extract_plain_text().strip():
        if name := server_manager.parse_server(args):
            message = turn_message(detailed_handler(name))
            await matcher.finish(message)
        await matcher.finish(F'未找到服务器 [{args}]，请检查输入是否正确！或是因为服务器的 PID 没有被记录，请重启服务器后尝试。')
    message = turn_message(status_handler())
    await matcher.finish(message)


def find_font():
    for font_path in findSystemFonts():
        if 'KAITI' in font_path.upper():
            logger.success(F'自动选择系统字体 {font_path} 设为图表字体。')
            return FontProperties(fname=font_path, size=15)


def draw_chart(data: dict):
    logger.debug('正在绘制服务器占比柱状图……')
    pyplot.xlabel('Perventage(%)', loc='right')
    pyplot.title('Server Usage Percentage')
    for count, (cpu, ram) in enumerate(data.values()):
        pos = (count * 2)
        cpu_bar = pyplot.barh(pos, cpu, color='red')
        ram_bar = pyplot.barh(pos + 1, ram, color='blue')
    pyplot.legend((cpu_bar, ram_bar), ('CPU', 'RAM'))
    pyplot.yticks([(count * 2 + 0.5) for count in range(len(data))], data.keys(), fontproperties=font)
    buffer = BytesIO()
    pyplot.savefig(buffer, format='png')
    pyplot.clf()
    buffer.seek(0)
    return buffer


def draw_history_chart(name: str):
    logger.debug(F'正在绘制服务器 [{name}] 状态图表……')
    cpu = server_watcher.cpus.get(name)
    ram = server_watcher.rams.get(name)
    if len(cpu) >= 5:
        pyplot.ylim(0, 100)
        pyplot.xlabel('Time', loc='right')
        pyplot.ylabel('Percentage(%)', loc='top')
        pyplot.title('CPU & RAM Precentage')
        pyplot.plot(cpu, color='red', label='CPU')
        pyplot.plot(ram, color='blue', label='RAM')
        pyplot.legend()
        pyplot.grid()
        buffer = BytesIO()
        pyplot.savefig(buffer, format='png')
        pyplot.clf()
        buffer.seek(0)
        return buffer


def status_handler():
    if data := server_watcher.get_data():
        yield '已连接的所有服务器信息：'
        for name, (cpu, ram) in data.items():
            yield F'————— {name} —————'
            yield F'  内存使用率：{ram:.1f}%'
            yield F'  CPU 使用率：{cpu:.1f}%'
        yield '所有服务器的占用柱状图：'
        yield str(MessageSegment.image(draw_chart(data)))
        return None
    yield '当前没有被监视的服务器！'


def detailed_handler(server: str):
    if name := server_manager.parse_server(server):
        if data := server_watcher.get_data(name):
            cpu, ram = data
            yield F'服务器 [{name}] 的详细信息：'
            yield F'  内存使用率：{ram:.1f}%'
            yield F'  CPU 使用率：{cpu:.1f}%'
            if image := draw_history_chart(name):
                yield '服务器的占用历史记录：'
                yield str(MessageSegment.image(image))
                return None
            yield '未找到服务器的占用历史记录，无法绘制图表。请稍后再试！'
            return None
        yield F'服务器 [{name}] 未处于被监视状态！请重启服务器后尝试。'
        return None
