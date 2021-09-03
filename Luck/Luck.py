import json
# import random
import datetime
import hashlib
import os
from sys import modules

from graia.application import GraiaMiraiApplication
from graia.application.message.chain import MessageChain
from graia.application.message.elements.internal import Plain, Image

from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.application.event.messages import Group, Member, GroupMessage
from SAGIRIBOT.MessageSender.MessageSender import GroupMessageSender
from SAGIRIBOT.Handler.Handler import AbstractHandler
from SAGIRIBOT.MessageSender.MessageItem import MessageItem
# from SAGIRIBOT.MessageSender.MessageSender import set_result
from SAGIRIBOT.MessageSender.Strategy import GroupStrategy, Normal, QuoteSource
from SAGIRIBOT.utils import update_user_call_count_plus1, UserCalledCount
from SAGIRIBOT.utils import MessageChainUtils

saya = Saya.current()
channel = Channel.current()

@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def abbreviated_prediction_handler(app: GraiaMiraiApplication, message: MessageChain, group: Group,
                                         member: Member):
    if result := await SensojiLuck.handle(app, message, group, member):
        await GroupMessageSender(result.strategy).send(app, result.message, message, group, member)

class SensojiLuck(AbstractHandler):
    __name__ = "SensojiLuck"
    __description__ = "浅草寺求签，copy自獭爹的bot(https://github.com/Bluefissure/OtterBot)"
    __usage__ = ""

    @staticmethod
    async def handle(app: GraiaMiraiApplication, message: MessageChain, group: Group, member: Member):
        if message.asDisplay() == "求签" or message.asDisplay() == "电子观音" or message.asDisplay() == "仿生阿强":
            await update_user_call_count_plus1(group, member, UserCalledCount.functions, "functions")
            return await SensojiLuck.get_luck(member.id)
        else:
            return None

    @staticmethod
    async def get_luck(qqNum):
        random_num = await SensojiLuck.get_page_num(qqNum)
        path = os.path.join(f"{os.getcwd()}", "modules", "Luck", "Luck.json")
        with open(path, 'r', encoding='utf-8') as luck_data:
            data = json.load(luck_data)[random_num]['fields']['text']
        formatt_data = ["---每人每天可以抽一次哟---\n\n"]
        formatt_data.append(data)
        formatt_data.append('抽到凶签也不要气馁，明天还可以继续抽喔')
        content = "".join(formatt_data)
        # 转图片发送
        return MessageItem(await MessageChainUtils.messagechain_to_img(MessageChain.create([Plain(text=content)]), font_size=50), QuoteSource(GroupStrategy()))
        # 直接发送文字
        # return MessageItem(MessageChain.create([Plain(text=content)]), Normal(GroupStrategy()))

    @staticmethod
    async def get_page_num(qqNum):
        today = datetime.date.today()
        formatted_today = int(today.strftime('%y%m%d'))
        strnum = str(formatted_today * qqNum)

        md5 = hashlib.md5()
        md5.update(strnum.encode('utf-8'))
        res = md5.hexdigest()

        return int(res.upper(), 16) % 100


