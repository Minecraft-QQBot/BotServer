from openai import AsyncClient
from openai import RateLimitError, BadRequestError

from nonebot import on_message
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment, Bot
from nonebot.log import logger
from nonebot.rule import to_me

from Scripts.Config import config
from Scripts.Utils import Rules, get_permission

logger.debug('加载 Ai 功能完毕！')
messages = [{'role': 'system', 'content': config.ai_system_prompt}]
client = AsyncClient(base_url=config.ai_base_url, api_key=config.ai_api_key)

matcher = on_message(rule=to_me() & Rules.command_rule, priority=15, block=False)


@matcher.handle()
async def handle_message(bot: Bot, event: GroupMessageEvent):
    plain_text = event.get_plaintext()
    if plain_text.strip() in ('清空缓存', '清除缓存'):
        if not get_permission(event):
            await matcher.finish('你没有权限执行此操作！')
        await clear()
        await matcher.finish('缓存已清空！')
    # await upload_file(event.original_message, bot)
    if plain_text:
        messages.append({'role': 'user', 'content': plain_text})
    try:
        completion = await client.chat.completions.create(
            messages=messages, model=config.ai_model_name, temperature=0.3
        )
    except RateLimitError:
        await matcher.finish(MessageSegment.reply(event.message_id) + '啊哦！你问的太快啦，我的脑袋转不过来了 TwT')
    except BadRequestError as error:
        await matcher.finish(MessageSegment.reply(event.message_id) + F'啊哦！遇到错误：{error.message}')
    response = completion.choices[0]
    if text := response.message.content:
        messages.append(dict(response.message))
        await matcher.finish(MessageSegment.reply(event.message_id) + text)
    await matcher.finish(MessageSegment.reply(event.message_id) + '呃？你在说什么，能不能重新说一下 T_T')


async def clear():
    messages.clear()
    file_list = await client.files.list()
    for file in file_list.data:
        await client.files.delete(file.id)


# async def upload_file(message: Message, bot: Bot):
#     file_segments = []
#     for segment in message:
#         if segment.type == 'image':
#             file_segments.append(segment.data)
#         elif segment.type == 'reply':
#             message = await bot.get_msg(message_id=segment.data['id'])
#             logger.info(F'正在解析引用消息 {message} 的文件……')
#             for reply_segment in message.get('message', []):
#                 if reply_segment['type'] in ('image', 'file'):
#                     file_segments.append(reply_segment['data'])
#     if file_segments:
#         logger.debug(F'上传文件：{file_segments}')
#         with TemporaryDirectory() as temp_path:
#             temp_path = Path(temp_path)
#             for segment_data in file_segments:
#                 if file := await download(segment_data['url']):
#                     path = (temp_path / segment_data['filename'])
#                     with path.open('wb') as download_file:
#                         download_file.write(file.getvalue())
#                     file = await client.files.create(file=path, purpose='file-extract')
#                     file_content = await client.files.content(file.id)
#                     messages.append({'role': 'system', 'content': file_content.text})
#                     continue
#                 await matcher.send('下载文件失败！', at_sender=True)
