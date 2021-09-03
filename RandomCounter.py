from os import times
import random
# import asyncio
import re

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

saya = Saya.current()
channel = Channel.current()


@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def abbreviated_prediction_handler(app: GraiaMiraiApplication, message: MessageChain, group: Group,
                                         member: Member):
    if result := await RandomCount.handle(app, message, group, member):
        await GroupMessageSender(result.strategy).send(app, result.message, message, group, member)


class RandomCount():
    __name__ = "RandomCount"

    @staticmethod
    async def handle(app: GraiaMiraiApplication, message: MessageChain, group: Group, member: Member):
        if n := re.match(r'roll\s([1-9])d([1-9][0-9]?)', message.asDisplay()):
            times = int(n[1])
            dice = int(n[2])
            await update_user_call_count_plus1(group, member, UserCalledCount.functions, "functions")
            return await RandomCount.roll_dice(times, dice)
        else:
            return None

    @staticmethod
    async def roll_dice(times=1, dice=20):
        res = []
        for i in range(times):
            roll = random.randint(1, dice)
            res.append(roll)
        content = "".join(str(res))
        return MessageItem(MessageChain.create([Plain(text=content)]),
                           QuoteSource(GroupStrategy()))
