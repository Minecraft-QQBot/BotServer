from nonebot import on_command
from nonebot.adapters.onebot.v11 import PrivateMessageEvent, GroupMessageEvent


mather = on_command('你的指令名称')


# 群指令处理器，若不需要可删除
@mather.handle()
async def handle_group(event: GroupMessageEvent):
    # 发送消息 详细见 https://nonebot.dev/docs/
    await mather.finish('这是一个测试')

# 私聊指令处理器，若不需要可删除
@mather.handle()
async def handle_private(event: PrivateMessageEvent):
    # 发送消息
    await mather.finish('这是一个测试')

# 主要处理函数
async def main_handle():
    pass
    # 你的函数逻辑
