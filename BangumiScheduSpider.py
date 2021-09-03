import asyncio
import re
import aiohttp
from bs4 import BeautifulSoup

from graia.saya import Saya, Channel
from graia.application import GraiaMiraiApplication
from graia.application.message.chain import MessageChain
from graia.application.message.elements.internal import Plain
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.application.event.messages import Group, Member, GroupMessage

from SAGIRIBOT.utils import MessageChainUtils
from SAGIRIBOT.MessageSender.Strategy import Normal
from SAGIRIBOT.MessageSender.Strategy import GroupStrategy
from SAGIRIBOT.MessageSender.MessageItem import MessageItem
from SAGIRIBOT.MessageSender.MessageSender import GroupMessageSender
from aiohttp.client import TCPConnector

saya = Saya.current()
channel = Channel.current()


@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def abbreviated_prediction_handler(app: GraiaMiraiApplication, message: MessageChain, group: Group,
                                         member: Member):
    if result := await BangumiSpider.handle(app, message, group, member):
        await GroupMessageSender(result.strategy).send(app, result.message, message, group, member)


# python aiohttpSpider.py

findtitle = re.compile(r'<h3 class="subtitle is-6 mb-0">(.*?)</h3>', re.S)
findtime = re.compile(r'<span class="has-text-grey bgm-item--meta-title">(.*?)：</span>', re.S)
findresource_title1 = re.compile(r'target="_blank">(.*?)</a>')
findresource_title2 = re.compile(r'title="(.*?)"')
findlink = re.compile(r'href=(.*?)target')
findnumber = re.compile(r'<span>(.*?)</span>', re.S)


def dont_have_class_and_target(tag):
    return not tag.has_attr('class') and not tag.has_attr('target')


class BangumiSpider():
    __name__ = "BangumiSpider"
    __description__ = "从番组计划网页中爬取新番信息"
    __usage__ = "在群中发送周[1-8]新番，或[本当今]日新番，获取新番信息表；发送周[1-8]第[n]部链接，获取那天第n部新番的链接"

    @staticmethod
    async def handle(app: GraiaMiraiApplication, message: MessageChain, group: Group, member: Member):
        if n := re.match(r"周([1-7])新番", message.asDisplay()):
            weekday = int(n[1])
            return await BangumiSpider.formatted_output_bangumi(weekday)
        elif re.match(r"[本当今]日新番", message.asDisplay()):
            weekday = 8
            return await BangumiSpider.formatted_output_bangumi(weekday)
        elif n := re.match(r"周([1-8])第([0-9]{1,2})部(链接)?", message.asDisplay()):
            weekday = int(n[1])
            num = int(n[2])
            return await BangumiSpider.formatted_output_bangumi_link(weekday, num - 1)
        elif n := re.match(r"今日第([0-9]*)部(链接)?", message.asDisplay()):
            weekday = 8
            num = int(n[1])
            return await BangumiSpider.formatted_output_bangumi_link(weekday, num - 1)
        else:
            return None

    async def get_bangumi_schedule(self, weekday=8):
        baseurl = "https://bgm.ideapart.com"
        head = {
            "User-Agent": "Mozilla / 5.0(Windows NT 10.0; Win64; x64) AppleWebKit / 537.36(KHTML, like Gecko) Chrome / 80.0.3987.122  Safari / 537.36"}
        if weekday == 8:
            url = baseurl
        elif weekday == 0:
            url = baseurl + "/?weekday=" + str(weekday)
        elif weekday == 7:
            url = baseurl + "/?weekday=1"
        else:
            url = baseurl + "/?weekday=" + str(weekday + 1)
        async with aiohttp.ClientSession(connector=TCPConnector(verify_ssl=False)) as session:
            async with session.get(url, headers=head) as res:
                html = await res.read()
                return html

    async def get_data(self, html) -> list:
        try:
            soup = BeautifulSoup(html, 'html.parser')
            datalist = []
            for item in soup.find_all('div',
                                      class_="bgm-item--main is-flex is-flex-direction-column is-justify-content-space-between"):
                title = item.find_all("h3", class_="subtitle is-6 mb-0")
                title_data = re.findall(findtitle, str(title))

                time = item.find_all("span", class_="has-text-grey bgm-item--meta-title")
                time_data = re.findall(findtime, str(time))

                number = item.find_all(dont_have_class_and_target)
                number_data = re.findall(findnumber, str(number))

                resource_title = item.find_all("span", class_="bgm-item--meta-content")
                title1 = re.findall(findresource_title1, str(resource_title))
                title2 = re.findall(findresource_title2, str(resource_title))
                titles = title1 + title2
                links = re.findall(findlink, str(resource_title))
                titles_and_links = []

                for k in range(len(titles)):
                    titles_and_links.append(titles[k] + ":" + links[k])
                data_json = {"name": title_data, "time": time_data, "howmach": number_data,
                             "resource": titles_and_links}
                datalist.append(data_json)
                # print(data_json)
            # print(datalist)
            return datalist
        except Exception as e:
            raise e

    async def get_list(self, weekday: int) -> list:
        html = await BangumiSpider().get_bangumi_schedule(weekday)
        res = await BangumiSpider().get_data(html)
        return res

    def main(self):
        loop = asyncio.get_event_loop()
        html = loop.run_until_complete(BangumiSpider().get_bangumi_schedule())
        res = loop.run_until_complete(BangumiSpider().get_data(html))
        print(res)

    @staticmethod
    async def formatted_output_bangumi(weekday: int) -> MessageItem:
        """
        Formatted output json data

        Args:
            days: The number of days to output(1-7)

        Examples:
            data_str = formatted_output_bangumi(7)

        Return:
            MessageChain
            :param weekday:
        """
        formatted_bangumi_data = await BangumiSpider().get_list(weekday)
        temp_output_substring = ["------------BANGUMI------------\n\n"]
        count = 1
        for data in formatted_bangumi_data:
            temp_output_substring.append(
                "[%d]\n番剧名：%s\n播出时间：%s\n当前集数：%s" % (count, data['name'], data['time'], data['howmach']))
            count += 1
            temp_output_substring.append("\n")
        temp_output_substring.append("\n数据来源：https://bgm.ideapart.com")
        content = "".join(temp_output_substring)
        return MessageItem(
            await MessageChainUtils.messagechain_to_img(MessageChain.create([Plain(text=content)])),
            Normal(GroupStrategy())
        )

    @staticmethod
    async def formatted_output_bangumi_link(weekday: int, num: int) -> MessageItem:
        """
        Formatted output json data

        Args:
            days: The number of days to output(1-7)

        Examples:
            data_str = formatted_output_bangumi(7)

        Return:
            MessageChain
            :param num:
            :param weekday:
        """
        formatted_bangumi_data = await BangumiSpider().get_list(weekday)
        if num >= len(formatted_bangumi_data):
            temp_output_substring = ["没有这部番哦~~~"]
        else:
            data = formatted_bangumi_data[num]
            temp_output_substring = ["------BANGUMI------\n"]
            temp_output_substring.append(
                "番剧名：%s\n播出时间：%s\n当前播出集数%s\n资源：\n%s" % (data['name'], data['time'], data['howmach'], data['resource']))
        temp_output_substring.append("\n数据来源：https://bgm.ideapart.com")
        content = "".join(temp_output_substring)
        return MessageItem(MessageChain.create([Plain(text=content)]),
                           Normal(GroupStrategy())
                           )
