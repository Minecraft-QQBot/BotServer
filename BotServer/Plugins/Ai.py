from nonebot import on_message
from nonebot.rule import to_me
from nonebot.adapters.onebot.v11 import GroupMessageEvent

from Scripts.Utils import Rules
from Scripts.Config import config

if config.ai_enable:
    from openai import RateLimitError, OpenAI

    client = OpenAI(base_url='https://api.moonshot.cn/v1', api_key='ApiKey')
    system_message = {'role': 'system', 'content': '你是小依，18岁的少男，温柔可爱，很招人喜欢。'}

    matcher = on_message(rule=to_me() & Rules.command_rule)


    @matcher.handle()
    async def handle_message(event: GroupMessageEvent):
        user_message = {'role': 'user', 'content': event.get_plaintext()}
        messages = (user_message, system_message)
        try:
            completion = client.chat.completions.create(messages=messages, model='moonshot-v1-8k', temperature=0.3)
        except RateLimitError:
            await matcher.finish('啊哦！你问的太快啦，我的脑袋转不过来了 TwT', at_sender=True)
        await matcher.finish(completion.choices[0].message.content, at_sender=True)
