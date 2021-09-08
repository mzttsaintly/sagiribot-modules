import re
import aiohttp
import asyncio

from aiohttp.client_exceptions import ClientConnectorError, ClientError    
    
api_key = "51ab2ac07ec94b70bfa24911a83cc1ff"

class Getweath():
    __name__ = "Getweath"

    @staticmethod
    async def handle(name: str):
        # if n := re.match(r'(.*)天气', message.asDisplay(), re.I):
        #     if n[1]:
        #         pass
        #     else:
        #         return MessageItem(MessageChain.create([Plain(text="地点是...空气吗？")]), Normal(GroupStrategy()))
        pass
        
        
        

    @staticmethod
    async def getweath(Lname, keyword="now"):
        url_weather_api = "https://devapi.qweather.com/v7/weather/"
        code, city_id, city_name = await Getweath.getlocation(Lname)
        if code == "200":
            async with aiohttp.ClientSession() as session:
                async with session.get(url_weather_api + keyword, params={"location": city_id, "key": api_key}) as res_session:
                    res = await res_session.json()
                    print(res)
                    return res, city_name
        else:
            return code, city_name
                

    @staticmethod
    async def getlocation(Lname: str, api_type: str ="lookup"):
        url_geoapi = "https://geoapi.qweather.com/v2/city/"
        async with aiohttp.ClientSession() as session:
            async with session.get(url_geoapi + api_type, params={"location": Lname, "key": api_key}) as res_session:
                res = await res_session.json()
                print(res)
                
                if res["code"] == "200":
                    location_id = res["location"][0]["id"]
                    city_name = res["location"][0]["name"]
                    return "200", location_id, city_name
                else:
                    return res, None, Lname

    @staticmethod
    async def nowweather(city_name: str, keyword: str="now"):
        data, city_name = await Getweath.getweath(city_name, keyword)
        if data["code"] == "200":
            now = data["now"]
            message = ["------实时天气数据------\n\n"]
            message.append("城市：%s\n温度（℃）：%s\n体感温度（℃）：%s\n天气情况：%s\n风向：%s\n风力：%s\n风速（km/h）：%s\n相对湿度：%s\n云量：%s\n能见度：%s\n大气压强（百帕）：%s\n" % (city_name, now["temp"], now["feelsLike"], now["text"], now["windDir"], now["windScale"], now["windSpeed"], now["humidity"], now["cloud"], now["vis"], now["pressure"]))
            message.append("数据来源：和风天气\n")
            message.append("数据更新时间：%s\n" % data["updateTime"])
            message.append("链接：%s" % data["fxLink"])
            content = "".join(message)
            return content
        else:
            return "错误代码：%s" % data["code"]

    @staticmethod
    async def thirddayweather(city_name: str, keyword: str="3d"):
        data, city_name = await Getweath.getweath(city_name, keyword)
        if data['code'] == '200':
            day1 = data['daily'][0]
            day2 = data['daily'][1]
            day3 = data['daily'][2]
            message = ["------天气预报------\n"]
            message.append("地点： %s\n" % city_name)
            message.append("日期：%s\n最高温度（℃）：%s\n最低气温（℃）：%s\n日间天气情况：%s\n夜间天气情况：%s\n紫外线强度指数：%s\n\n" % (day1["fxDate"], day1["tempMax"], day1["tempMin"], day1["textDay"], day1["textNight"], day1["uvIndex"]))
            message.append("日期：%s\n最高温度（℃）：%s\n最低气温（℃）：%s\n日间天气情况：%s\n夜间天气情况：%s\n紫外线强度指数：%s\n\n" % (day2["fxDate"], day2["tempMax"], day2["tempMin"], day2["textDay"], day2["textNight"], day2["uvIndex"]))
            message.append("日期：%s\n最高温度（℃）：%s\n最低气温（℃）：%s\n日间天气情况：%s\n夜间天气情况：%s\n紫外线强度指数：%s\n\n" % (day3["fxDate"], day3["tempMax"], day3["tempMin"], day3["textDay"], day3["textNight"], day3["uvIndex"]))
            message.append("数据来源：和风天气\n")
            message.append("数据更新时间：%s\n" % data["updateTime"])
            message.append("链接：%s" % data["fxLink"])
            content = "".join(message)
            return content
        else:
            return "错误代码：%s" % data["code"]

# python test_qweather.py
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    ans = loop.run_until_complete((Getweath.thirddayweather("yingde")))
    # location_id = ans["location"][0]["id"]
    print(ans)