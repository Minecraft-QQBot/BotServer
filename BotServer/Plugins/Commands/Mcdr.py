from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message
from nonebot.log import logger
from nonebot.params import CommandArg

# 导入自定义的模块和函数
from Scripts.Managers import server_manager
from Scripts.Utils import Rules, get_permission, get_args

# 记录 'Mcdr' 命令加载完成的日志，用于调试
logger.debug('加载命令 Mcdr 完毕！')
# 定义 'mcdr' 命令的匹配器，包括命令名称和匹配规则
matcher = on_command('mcdr', force_whitespace=True, rule=Rules.command_rule)


# handle_group 函数处理 'mcdr' 命令的事件
@matcher.handle()
async def handle_group(event: GroupMessageEvent, args: Message = CommandArg()):
    # 检查用户是否有执行命令的权限
    if not get_permission(event):
        # 如果没有权限，则结束命令并返回错误信息
        await matcher.finish('你没有权限执行此命令！')
    # 处理命令并获取返回信息
    message = await mcdr_handler(get_args(args))
    # 结束命令并返回处理结果
    await matcher.finish(message)


# mcdr_handler 函数处理 'mcdr' 命令的具体逻辑
async def mcdr_handler(args: list):
    # 检查参数是否正确
    if len(args) <= 1:
        return '参数不正确！请查看语法后再试。'
    # 解析服务器标识和命令
    server_flag, *command = args
    command = ' '.join(command)
    # 确保命令以 '!!' 开头
    if not command.startswith('!!'):
        command = ('!!' + command)
    # 发送命令到所有已连接的服务器
    if server_flag == '*':
        await server_manager.execute_mcdr(command)
        return '命令已发送到所有已连接的服务器！'
    # 发送命令到指定服务器
    if server := server_manager.get_server(server_flag):
        await server.send_mcdr_command(command)
        return F'命令发送到服务器 [{server.name}] 完毕！'
    # 未找到指定的服务器
    return F'服务器 [{server_flag}] 不存在！'
