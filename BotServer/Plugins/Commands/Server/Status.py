# 导入必要的模块
from io import BytesIO
from os.path import exists

from matplotlib import pyplot
from matplotlib.font_manager import findSystemFonts, FontProperties
from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageEvent, MessageSegment, Message
from nonebot.log import logger
from nonebot.params import CommandArg

# 导入全局变量和自定义模块
import Globals
from Scripts.Managers import server_manager
from Scripts.Utils import Rules, turn_message


# 选择并返回一个可用的字体，优先使用本地字体文件，其次自动选择系统中的楷体
def choose_font():
    # 尝试加载本地字体文件
    for font_format in ('ttf', 'ttc'):
        if exists(F'./Font.{font_format}'):
            logger.info(F'已找到用户设置字体文件，将自动选择该字体作为图表字体。')
            return FontProperties(fname=F'./Font.{font_format}', size=15)
    # 如果本地字体文件不存在，尝试从系统字体中选择楷体
    for font_path in findSystemFonts():
        if 'KAITI' in font_path.upper():
            logger.success(F'自动选择系统字体 {font_path} 设为图表字体。')
            return FontProperties(fname=font_path, size=15)


# 使用选择的字体初始化全局变量font
font = choose_font()

# 初始化命令匹配器，用于处理'/server status'命令
matcher = on_command('server status', force_whitespace=True, block=True, priority=5, rule=Rules.command_rule)


# 处理'/server status'命令的事件响应
@matcher.handle()
async def handle_group(event: MessageEvent, args: Message = CommandArg()):
    # 检查用户是否提供了服务器标识符
    if args := args.extract_plain_text().strip():
        flag, response = await get_status(args)
        if flag is False:
            await matcher.finish(response)
        message = turn_message(detailed_handler(flag, response))
        await matcher.finish(message)
    # 如果没有提供服务器标识符，获取默认状态
    flag, response = await get_status()
    if flag is False:
        await matcher.finish(response)
    logger.error(response)
    message = turn_message(status_handler(response))
    await matcher.finish(message)


# 处理所有服务器状态信息的函数
def status_handler(data: dict):
    yield '已连接的所有服务器信息：'
    for name, occupation in data.items():
        yield F'————— {name} —————'
        if occupation:
            cpu, ram = occupation
            yield F'  内存使用率：{ram:.1f}%'
            yield F'  CPU 使用率：{cpu:.1f}%'
            continue
        yield F'  此服务器未处于监视状态！'
    # 检查是否找到可用字体，如果没有，提示用户
    if font is None:
        yield '\n由于系统中没有找到可用的中文字体，无法显示中文标题。请查看文档自行配置！'
        return None
    # 如果所有服务器都不在监视状态，无法绘制柱状图
    if not any(data.values()):
        yield '\n当前没有服务器处于监视状态！无法绘制柱状图。'
    # 绘制并发送所有服务器的占用柱状图
    yield '\n所有服务器的占用柱状图：'
    yield str(MessageSegment.image(draw_chart(data)))
    return None


# 处理单个服务器详细状态信息的函数
def detailed_handler(name: str, data: list):
    cpu, ram = data
    # 格式化服务器的详细状态信息
    yield F'服务器 [{name}] 的详细信息：'
    yield F'  内存使用率：{ram:.1f}%'
    yield F'  CPU 使用率：{cpu:.1f}%'
    # 如果存在历史数据，绘制并发送服务器的占用历史记录图表
    if image := draw_history_chart(name):
        yield '\n服务器的占用历史记录：'
        yield str(MessageSegment.image(image))
        return None
    # 如果没有历史数据，提示用户
    yield '\n未找到服务器的占用历史记录，无法绘制图表。请稍后再试！'
    return None


# 绘制服务器占用情况的柱状图
def draw_chart(data: dict):
    count, names = 0, []
    cpu_bar, ram_bar = None, None
    logger.debug('正在绘制服务器占比柱状图……')
    pyplot.xlabel('Percentage(%)', loc='right')
    pyplot.title('Server Usage Percentage')
    # 遍历数据，绘制每个服务器的CPU和内存占用柱状图
    for name, occupation in data.items():
        if occupation:
            pos = (count * 2)
            cpu, ram = occupation
            names.append(name)
            cpu_bar = pyplot.barh(pos, cpu, color='red')
            ram_bar = pyplot.barh(pos + 1, ram, color='blue')
            count += 1
    pyplot.legend((cpu_bar, ram_bar), ('CPU', 'RAM'))
    pyplot.yticks([(count * 2 + 0.5) for count in range(len(names))], names, fontproperties=font)
    buffer = BytesIO()
    pyplot.savefig(buffer, format='png')
    pyplot.clf()
    buffer.seek(0)
    return buffer


# 绘制指定服务器的历史占用情况图表
def draw_history_chart(name: str):
    logger.debug(F'正在绘制服务器 [{name}] 状态图表……')
    cpu = Globals.cpu_occupation.get(name)
    ram = Globals.ram_occupation.get(name)
    # 确保数据点足够绘制图表
    if len(cpu) >= 5:
        pyplot.ylim(0, 100)
        pyplot.xlabel('Time', loc='right')
        pyplot.ylabel('Percentage(%)', loc='top')
        pyplot.title('CPU & RAM Percentage')
        pyplot.plot(cpu, color='red', label='CPU')
        pyplot.plot(ram, color='blue', label='RAM')
        pyplot.legend()
        pyplot.grid()
        buffer = BytesIO()
        pyplot.savefig(buffer, format='png')
        pyplot.clf()
        buffer.seek(0)
        return buffer


# 获取服务器占用情况的异步函数，可以针对特定服务器或所有服务器
async def get_status(server_flag: str = None):
    # 如果没有指定服务器标识符，返回所有已连接服务器的占用情况
    if server_flag is None:
        if data := await server_manager.get_server_occupation():
            return True, data
        return False, '当前没有已连接的服务器！'
    # 如果指定了服务器标识符，尝试获取该服务器的占用情况
    if server := server_manager.get_server(server_flag):
        if data := await server.send_server_occupation():
            return server.name, data
        return False, F'服务器 [{server_flag}] 未处于监视状态！请重启服务器后再试。'
    return False, F'服务器 [{server_flag}] 未找到！请重启服务器后尝试。'
