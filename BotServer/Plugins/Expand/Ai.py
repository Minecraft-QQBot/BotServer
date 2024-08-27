from pathlib import Path
from tempfile import TemporaryDirectory

from nonebot import on_message
from nonebot.rule import to_me
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment

from Globals import openai
from Scripts.Network import download
from Scripts.Utils import Rules, get_permission
from Scripts.Config import config

logger.debug('加载 Ai 功能完毕！')
messages = [{'role': 'system', 'content': config.ai_role_message}]
matcher = on_message(rule=to_me() & Rules.command_rule, priority=15, block=False, )


async def upload_file(message):
    file_segments = [segment for segment in message if segment.type in ('image', 'file')]
    if file_segments:
        with TemporaryDirectory() as temp_path:
            temp_path = Path(temp_path)
            for segment in file_segments:
                if file := await download(segment.data['url']):
                    path = (temp_path / segment.data['filename'])
                    with path.open('wb') as download_file:
                        download_file.write(file.getvalue())
                    file = await client.files.create(file=path, purpose='file-extract')
                    file_content = await client.files.content(file.id)
                    messages.append({'role': 'system', 'content': file_content.text})
                    continue
                await matcher.send('下载文件失败！', at_sender=True)


if config.ai_enabled:
    client = openai.AsyncClient(base_url='https://api.moonshot.cn/v1', api_key=config.ai_api_key)

    @matcher.handle()
    async def handle_message(event: GroupMessageEvent):
        plain_text = event.get_plaintext()
        if plain_text.strip() in ('清空缓存', '清除缓存'):
            if not get_permission(event):
                await matcher.finish('你没有权限执行此操作！')
            messages.clear()
            file_list = await client.files.list()
            for file in file_list.data:
                await client.files.delete(file.id)
            await matcher.finish('缓存已清除！')
        await upload_file(event.message)
        if plain_text:
            messages.append({'role': 'user', 'content': plain_text})
        try:
            completion = await client.chat.completions.create(
                messages=messages, model='moonshot-v1-8k', temperature=0.3
            )
        except openai.RateLimitError:
            await matcher.finish(MessageSegment.reply(event.message_id) + '啊哦！你问的太快啦，我的脑袋转不过来了 TwT')
        except openai.BadRequestError as error:
            await matcher.finish(MessageSegment.reply(event.message_id) + F'啊哦！遇到错误：{error.message}')
        response = completion.choices[0]
        messages.append(dict(response.message))
        await matcher.finish(MessageSegment.reply(event.message_id) + response.message.content)
