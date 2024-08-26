# 导入所需的库和模块
from nonebot import on_message
from nonebot.rule import to_me
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment

# 导入全局变量和自定义模块
from Globals import openai
from Scripts.Network import download
from Scripts.Utils import Rules, get_permission
from Scripts.Config import config

# 初始化消息记录，用于上下文对话
messages = [{'role': 'system', 'content': config.ai_role_message}]
# 定义消息匹配器，仅当消息单独提到机器人时且符合自定义规则时触发
matcher = on_message(rule=to_me() & Rules.command_rule, priority=15, block=False)

# 如果配置了AI功能，则进行初始化
if config.ai_enabled:

    # 创建OpenAI客户端，用于后续的API调用
    client = openai.AsyncClient(base_url='https://api.moonshot.cn/v1', api_key=config.ai_api_key)


    # 定义消息处理函数
    @matcher.handle()
    async def handle_message(event: GroupMessageEvent):
        # 获取消息的纯文本内容
        plain_text = event.get_plaintext()
        # 检查是否需要清除缓存
        if plain_text.strip() == '清除缓存':
            # 检查用户权限
            if not get_permission(event):
                await matcher.finish('你没有权限执行此操作！')
            # 清除本地消息记录
            messages.clear()
            # 清除远程文件存储
            file_list = await client.files.list()
            for file in file_list.data:
                await client.files.delete(file.id)
            await matcher.finish('缓存已清除！')
        # 处理消息中的图片或文件
        for segment in event.message:
            if segment.type in ('image', 'file'):
                file = await download(segment.data['url'])
                file = await client.files.create(file=file, purpose='file-extract')
                file_content = await client.files.content(file.id)
                # 将文件内容添加到消息记录中
                messages.append({'role': 'system', 'content': file_content.text})
        # 将用户消息添加到消息记录中
        messages.append({'role': 'user', 'content': plain_text})
        try:
            # 使用OpenAI API生成回复
            completion = await client.chat.completions.create(
                messages=messages, model='moonshot-v1-8k', temperature=0.3
            )
        except openai.RateLimitError:
            # 如果API调用频率限制，发送消息并结束会话
            await matcher.finish(MessageSegment.reply(event.message_id) + '啊哦！你问的太快啦，我的脑袋转不过来了 TwT')
        # 获取API回复的内容
        response = completion.choices[0]
        # 将回复内容添加到消息记录中
        messages.append(dict(response.message))
        # 发送回复消息并结束会话
        await matcher.finish(MessageSegment.reply(event.message_id) + response.message.content)
