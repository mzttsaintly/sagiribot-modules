import asyncio
import re
import aiohttp
import json
# from bs4 import BeautifulSoup

from graia.saya import Saya, Channel
from graia.application import GraiaMiraiApplication
from graia.application.message.chain import MessageChain
from graia.application.message.elements.internal import Plain, At
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.application.event.messages import Group, Member, GroupMessage

from SAGIRIBOT.utils import MessageChainUtils
from SAGIRIBOT.MessageSender.Strategy import Normal
from SAGIRIBOT.MessageSender.Strategy import GroupStrategy
from SAGIRIBOT.MessageSender.MessageItem import MessageItem
from SAGIRIBOT.MessageSender.MessageSender import GroupMessageSender
from SAGIRIBOT.utils import get_config
# from SAGIRIBOT.utils import update_user_call_count_plus1, UserCalledCount

saya = Saya.current()
channel = Channel.current()

@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def abbreviated_prediction_handler(app: GraiaMiraiApplication, message: MessageChain, group: Group, member: Member):
    if result := await Saohua.handle(app, message, group, member):
        await GroupMessageSender(result.strategy).send(app, result.message, message, group, member)

class Saohua:
    __name__ == "__Saohua"

    @staticmethod
    async def handle(app: GraiaMiraiApplication, message: MessageChain, group: Group, member: Member):
        if message.asDisplay() == "来点骚话":
            return await Saohua.get_saohua()
        elif message.has(At) and message.get(At)[0].target == get_config("BotQQ"):
            return await Saohua.get_saohua()
        else:
            return None

    @staticmethod
    async def get_html():
        url = "https://api.kotori.love/hitokoto/json"
        head = {"User-Agent": "Mozilla / 5.0(Windows NT 10.0; Win64; x64) AppleWebKit / 537.36(KHTML, like Gecko) Chrome / 80.0.3987.122  Safari / 537.36"}
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as res:
                html = await res.json()
                return html

    @staticmethod
    async def get_saohua():
        data = await Saohua.get_html()
        res = list()
        res.append("%s \n %s——%s" % (data['response']['data']['hitokoto'], data['response']['data']['source'], data['response']['data']['catname']))
        content = "".join(res)
        return MessageItem(MessageChain.create([Plain(text=content)]),
            Normal(GroupStrategy())
        )

#test
#python ./Saohua.py
# if __name__ == "__main__":
#     loop = asyncio.get_event_loop()
#     res = loop.run_until_complete(Saohua.get_saohua())
#     print(res)