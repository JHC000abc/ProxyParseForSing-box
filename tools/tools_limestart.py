# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@author: JHC000abc@gmail.com
@file: tools_limestart.py
@time: 2025/8/26 18:27 
@desc: 
    使用青柠起始页便签功能存储url 省的买服务器了
"""
import asyncio
import json
import argparse
from utils.utils_network import UtilsNetwork


class ToolsLimeStart:
    """

    """

    def __init__(self, token="3f57145f726f3a6acf8c974fbf5b1177", user_name="jhc000abct1ljk9ip"):
        self.net = UtilsNetwork()
        self.url = "https://api.limestart.cn/backend/note-v3"
        self.headers = {
            "accept": "*/*",
            "accept-language": "zh,zh-CN;q=0.9",
            "authorization": f"Bearer {token}",
            "content-type": "application/json",
            "origin": "https://www.limestart.cn",
            "referer": "https://www.limestart.cn/",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
        }
        self.user_name = user_name

    async def save_url(self, url):
        """

        :param url:
        :return:
        """
        data = {
            "content": f"{url}",
            "itemType": "txt",
            "username": f"{self.user_name}"
        }

        flag = False
        try:
            res = await self.net.fetch_url_post(self.url, headers=self.headers, data=data)
            id = json.loads(res)["id"]
            if id:
                flag = True
                return flag
        except:
            pass
        return flag

    async def get_latest_url(self):
        """

        :return:
        """
        params = {
            "username": f"{self.user_name}"
        }
        try:
            res = await self.net.fetch_url_get(self.url, headers=self.headers, params=params)
            for result in json.loads(res)["results"]:
                content = result["content"]
                return content
        except:
            pass
        return

    async def recode_url(self, url):
        """

        :param url:
        :return:
        """
        # 记录url
        if not await self.save_url(url):
            print("存储失败")
            return
        else:
            print(f"成功存储 url: {url}")

    async def get_url(self):
        """

        :return:
        """
        # 获取url
        latest_url = await self.get_latest_url()
        if not latest_url:
            print("获取最新链接失败")
            return
        else:
            print(f"{latest_url}")
            return latest_url

    async def clear(self):
        """

        :return:
        """
        params = {
            "username": f"{self.user_name}"
        }
        try:
            res = await self.net.fetch_url_get(self.url, headers=self.headers, params=params)
            data = json.loads(res)["results"]
            print(f"当前最新订阅链接:{data[0]['content']}")
            if len(data) <= 1:
                print("没有可删除的数据")
                return
            for ind, result in enumerate(data):
                if ind > 0:
                    id = result["id"]
                    content = result["content"]
                    params = {
                        "id": f"{id}",
                        "username": self.user_name
                    }
                    await self.net.fetch_url_delete(self.url, headers=self.headers, params=params)
                    print(f"删除:{content}")
        except:
            pass

    async def process(self, url):
        """

        :param url:
        :return:
        """


async def main():
    """

    :return:
    """
    # 上传记录工具
    t = ToolsLimeStart()
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', "--input", dest='input', help='input', required=True, nargs='+')
    args = parser.parse_args()
    urls = args.input
    for url in urls:
        await t.recode_url(url)

    # 获取最新记录工具
    # t = ToolsLimeStart()
    # await t.get_url()

    # 删除记录工具
    t = ToolsLimeStart()
    await t.clear()


if __name__ == '__main__':
    asyncio.run(main())
