from nonebot import on_message
from nonebot.rule import to_me
from nonebot.adapters.onebot.v11 import GroupMessageEvent

from Globals import openai
from Scripts.Utils import Rules
from Scripts.Config import config

if config.ai_enable:
    system_message = {'role': 'system', 'content': config.ai_system_message}
    client = openai.OpenAI(base_url='https://api.moonshot.cn/v1', api_key=config.ai_api_key)

    matcher = on_message(rule=to_me() & Rules.command_rule, block=False)


    @matcher.handle()
    async def handle_message(event: GroupMessageEvent):
        messages = ({'role': 'user', 'content': event.get_plaintext()}, system_message)
        try:
            completion = client.chat.completions.create(messages=messages, model='moonshot-v1-8k', temperature=0.3)
        except openai.RateLimitError:
            await matcher.finish('啊哦！你问的太快啦，我的脑袋转不过来了 TwT', at_sender=True)
        await matcher.finish(completion.choices[0].message.content, at_sender=True)
