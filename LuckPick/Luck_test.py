import json
import datetime
import hashlib
import os
import asyncio

# python ./modules_beta/Luck/Luck_test.py

class SensojiLuck():

    @staticmethod
    async def get_luck(qqNum):
        random_num = await SensojiLuck.get_page_num(qqNum)
        path = os.path.join(f"{os.getcwd()}", "modules_beta", "Luck", "Luck.json")
        with open(path, 'r', encoding='utf-8') as luck_data:
            data = json.load(luck_data)[random_num]['fields']['text']
        formatt_data = ["每天可以抽一次\n\n"]
        formatt_data.append(data)
        content = "".join(formatt_data)
        print(content)

    @staticmethod
    async def get_page_num(qqNum):
        today = datetime.date.today()
        formatted_today = int(today.strftime('%y%m%d'))
        strnum = str(formatted_today * qqNum)

        md5 = hashlib.md5()
        md5.update(strnum.encode('utf-8'))
        res = md5.hexdigest()

        return int(res.upper(), 16) % 100

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(SensojiLuck.get_luck(3613))