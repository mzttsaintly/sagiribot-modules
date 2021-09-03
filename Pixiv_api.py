import re
import random
import aiohttp
from aiohttp.client_exceptions import ClientConnectorError, ClientError

from graia.saya import Saya, Channel
from graia.application import GraiaMiraiApplication
from graia.application.message.chain import MessageChain
from graia.application.message.elements.internal import Plain, Image
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.application.event.messages import Group, Member, GroupMessage
from pydantic.class_validators import extract_validators

from SAGIRIBOT.MessageSender.Strategy import Normal
from SAGIRIBOT.MessageSender.Strategy import GroupStrategy
from SAGIRIBOT.MessageSender.MessageItem import MessageItem
from SAGIRIBOT.MessageSender.MessageSender import GroupMessageSender


saya = Saya.current()
channel = Channel.current()


@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def abbreviated_prediction_handler(app: GraiaMiraiApplication, message: MessageChain, group: Group,
                                         member: Member):
    if result := await GetPixiv.handle(app, message, group, member):
        await GroupMessageSender(result.strategy).send(app, result.message, message, group, member)


class GetPixiv:
    __name__ = "RandomCount"

    @staticmethod
    async def handle(app: GraiaMiraiApplication, message: MessageChain, group: Group, member: Member):
        if n := re.match(r'p站(.*?)榜([0-9]{0,2})?', message.asDisplay(), re.I) or re.match(r'pixiv\srank\s(.*)\s?([0-9]{0,2})?', message.asDisplay(), re.I):
            mode_dict = {"日": "day", "周": "week", "月": "month", "新人": "week_rookie", "原创": "week_original",
                         "男性向": "day_male", "女性向": "day_female", "day": "day", "week": "week",
                          "month": "month", "week_rookie": "week_rookie", "day_male": "day_male",
                           "day_female": "day_female"}
            if n[1] in mode_dict.keys():
                mode = mode_dict[n[1]]
                if n[2]:
                    num = int(n[2])
                    return await GetPixiv.search_rank(mode, num)
                else:
                    return await GetPixiv.search_rank(mode)
            else:
                return await GetPixiv.search_rank()
            
        elif n := re.match(r'p站(.*?)的图([0-9]{0,2})?', message.asDisplay(), re.I) or re.match(r'pixiv\skeyword[\s=](.*)([0-9]\s{0,2})?', message.asDisplay(), re.I):
            key_word = n[1]
            if n[2]:
                num = int(n[2])
                return await GetPixiv.search_word(key_word, num)
            else:
                return await GetPixiv.search_word(key_word)
        elif n := re.match(r'p站id[\s=]([0-9]*)', message.asDisplay(), re.I) or re.match(r'pixiv\sid[\s=]([0-9]*)', message.asDisplay(), re.I):
            key_word = int(n[1])
            return await GetPixiv.search_ID(key_word)
        else:
            return None


    @staticmethod
    async def get_html(function, keyword):
        baseurl = "https://api.obfs.dev/api/pixiv/{0}?{1}".format(function, keyword)
        con = aiohttp.TCPConnector(verify_ssl=False)
        try:
            async with aiohttp.ClientSession(connector=con) as session:
                async with session.get(baseurl) as res_session:
                    html = await res_session.json()
                    return html
        except Exception as e:
            return {"e:": "%s" % e, "illusts": None}



    @staticmethod
    async def revproxy(url):
        original_domain = "i.pximg.net"
        revproxy_domain = "i.pixiv.cat"
        rev_url = url.replace(original_domain, revproxy_domain)
        return rev_url


    @staticmethod
    async def search_rank(mode='day_male', num=0):
        function_name = "rank"
        key_word = "mode={}".format(mode)
        html = await GetPixiv.get_html(function_name, mode)
        try:
            illusts = html["illusts"]
            tot_num = len(illusts)
            if num < 1:
                illust = illusts[random.randint(0, tot_num - 1)]
            elif num > 50:
                return MessageItem(MessageChain.create([Plain(text="排名不可以大于50")]), Normal(GroupStrategy()))
            else:
                illust = illusts[num]
            img_url = illust["image_urls"]["large"]
            proxy_img_url = await GetPixiv.revproxy(img_url)
            return await GetPixiv.send_image("", proxy_img_url)
        except:
            return await GetPixiv.send_image(html)


    @staticmethod
    async def search_word(word="sagiri", num=0):
        function_name = "search"
        key_kord = "word={}".format(word)
        html = await GetPixiv.get_html(function_name, key_kord)
        try:
            illusts = html["illusts"]
            tot_num = len(illusts)
            if num < 1:
                illust = illusts[random.randint(0, tot_num - 1)]
            elif num > 50:
                return MessageItem(MessageChain.create([Plain(text="排名不可以大于50")]), Normal(GroupStrategy()))
            else:
                illust = illusts[num]
            img_url = illust["image_urls"]["large"]
            proxy_img_url = await GetPixiv.revproxy(img_url)
            return await GetPixiv.send_image("", proxy_img_url)
        except:
            return await GetPixiv.send_image(html)
        

    @staticmethod
    async def search_ID(id: int):
        function_name = "illust"
        key_word = "id={}".format(id)
        html = await GetPixiv.get_html(function_name, key_word)
        if "error" in html.keys():
            msg = html["error"]["user_message"] or html["error"]["message"]
            return await GetPixiv.send_image(str(msg))
        else:
            try:
                illust = html["illust"]
                img_url = illust["image_urls"]["large"]
                proxy_img_url = await GetPixiv.revproxy(img_url)
                return await GetPixiv.send_image("", proxy_img_url)
            except:
                return await GetPixiv.send_image(html)


    @staticmethod
    async def send_image(msg, image_url=None):
        try:
            if "code" in msg:
                if msg["code"] == 400:
                    return MessageItem(MessageChain.create([Plain(text="错误400：错误的请求")]), Normal(GroupStrategy()))
                elif msg["code"] == 422:
                    return MessageItem(MessageChain.create([Plain(text="错误422：无法处理")]), Normal(GroupStrategy()))
                elif msg["code"] == 500:
                    return MessageItem(MessageChain.create([Plain(text="错误500：内部服务器错误")]), Normal(GroupStrategy()))
                elif msg["code"] == 404:
                    return MessageItem(MessageChain.create([Plain(text="错误404：找不到图片")]), Normal(GroupStrategy()))
                elif msg["code"] == 502:
                    return MessageItem(MessageChain.create([Plain(text="错误502：不正确的网关")]), Normal(GroupStrategy()))
            if msg == "":
                message = MessageChain.create([
                    Image.fromNetworkAddress(image_url)
                ])
            elif image_url == None:
                message = MessageChain.create([Plain(text=msg)])
            else:
                message = MessageChain.create([
                    Plain(text=msg),
                    Image.fromNetworkAddress(image_url)
                ])
            return MessageItem(message, Normal(GroupStrategy()))
        except Exception as e:
            message = "%s" % str(e)
            return MessageItem(MessageChain.create([Plain(text=message)]), Normal(GroupStrategy()))


# test
# python ./Pixiv_api.py
# python ./modules_beta/Pixiv_api.py
# 图片代理：https://api.kotori.love/docs/#/pixiv
# i.pixiv.cat/
# 接口does https://api.obfs.dev/docs#operation/search_api_pixiv_search_get
# https://hibi.shadniw.ml/docs#operation/follower_api_pixiv_follower_get
