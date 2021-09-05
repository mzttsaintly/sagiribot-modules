import random
import os

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
# from SAGIRIBOT.utils import update_user_call_count_plus1, UserCalledCount
# from SAGIRIBOT.utils import MessageChainUtils
from SAGIRIBOT.utils import get_config

saya = Saya.current()
channel = Channel.current()


@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def abbreviated_prediction_handler(app: GraiaMiraiApplication, message: MessageChain, group: Group,
                                         member: Member):
    if result := await RandomImage.handle(app, message, group, member):
        await GroupMessageSender(result.strategy).send(app, result.message, message, group, member)


class RandomImage(AbstractHandler):
    __name__ = "__RandomImage__"
    __description__ = "从几个路径随机发图"
    __usage__ = "在群中发送'来点'"

    @staticmethod
    async def handle(app: GraiaMiraiApplication, message: MessageChain, group: Group, member: Member):
        if message.asDisplay() == "来点":
            return await RandomImage.get_image_message()
        elif n := re.match(r"hso[*=\s]?([0-9]*)?", message.asDisplay()):
            if n[1]:
                num = int(n[1])
                return await RandomImage.get_ten_image(num, "setu")
            else:
                return await RandomImage.get_ten_image(1, "setu")
        elif n := re.match(r"pw[*=\s]?([0-9]*)?", message.asDisplay()):
            if n[1]:
                num = int(n[1])
                return await RandomImage.get_ten_image(num, "wallpaper")
            else:
                return await RandomImage.get_ten_image(1, "wallpaper")
        else:
            return None

    @staticmethod
    async def get_image(kind="setu") -> Image:
        if kind == "setu":
            choice_kinds = random.choice(['setu', 'real'])
        elif kind == "wallpaper":
            choice_kinds = 'wallpaper'
        else:
            choice_kinds = random.choice(['setu', 'real', 'wallpaper'])
        image_path = f"{os.getcwd()}/statics/error/path_not_exists.png"
        if choice_kinds == 'setu':
            base_path = str(get_config("setuPath"))
            image_path = RandomImage.random_pic(base_path)
        if choice_kinds == 'real':
            base_path = str(get_config("realPath"))
            image_path = RandomImage.random_pic(base_path)
        if choice_kinds == 'wallpaper':
            base_path = str(get_config("wallpaperPath"))
            image_path = RandomImage.random_pic(base_path)
        return Image.fromLocalFile(image_path)

    @staticmethod
    def random_pic(base_path: str) -> str:
        path_dir = os.listdir(base_path)
        path = random.sample(path_dir, 1)[0]
        return base_path + path

    @staticmethod
    async def get_ten_image(num=1, kind="setu"):
        if 0 < num <= 10:
            image_list = []
            for i in range(num):
                image = await RandomImage.get_image(kind)
                image_list.append(image)
            return MessageItem(MessageChain.create(image_list), Normal(GroupStrategy()))
        else:
            return MessageItem(MessageChain.create([Plain(text="要得太多了可不给发的喔(上限是十张)")]), Normal(GroupStrategy()))

    @staticmethod
    async def get_image_message():
        return MessageItem(MessageChain.create([await RandomImage.get_image()]), Normal(GroupStrategy()))
