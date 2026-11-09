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
import requests
import base64
import hashlib
import time
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5

PUBLIC_KEY_PEM = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCxKxfpmroVBhtUjwoLK64188R7
Bsh+sCZTdH+zeu8OLR6tg/FHn7vIc0urqQ/lv8+gvmgbZ549BV80iOpXj/2vgpaj
vvkKJN6qgU0LLaoCEmZeJA79caY5Cym/qAS5VHRhzX4aHNinZtiwPUfaJwpW+4U2
h3xPsg5Wpd0CJDAtQwIDAQAB
-----END PUBLIC KEY-----"""


class Limestart:
    """

    """

    def __init__(self, password, user_name="jhc000abc@gmail.com"):
        self.user_name = user_name
        self.password = password

    def generate_encrypted(self) -> str:
        """

        :return:
        """
        # 1. MD5（32 位小写）
        md5_hash = hashlib.md5(self.password.encode("utf-8")).hexdigest()

        # 2. 当前毫秒时间戳
        timestamp = str(int(time.time() * 1000))

        # 3. 拼接
        payload = md5_hash + timestamp

        # 4. RSA PKCS#1 v1.5 加密
        rsa_key = RSA.import_key(PUBLIC_KEY_PEM)
        cipher = PKCS1_v1_5.new(rsa_key)
        encrypted_bytes = cipher.encrypt(payload.encode("utf-8"))

        # 5. Base64
        return base64.b64encode(encrypted_bytes).decode("utf-8")

    def login(self):
        """

        :param encrypted:
        :return:
        """
        body = {
            "encrypted": self.generate_encrypted(),
            "referrer": "https://www.limestart.cn/",
            "user": f"{self.user_name}"
        }
        headers = {
            "origin": "https://account.retiehe.com",
            "referer": "https://account.retiehe.com/",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36"
        }
        url = 'https://api.retiehe.com/backend/account-v2/session'
        response = requests.post(url, headers=headers, json=body)
        return response.json()


class ToolsLimeStart:
    """

    """

    def __init__(self, token, user_name):
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
    password = ""
    user_name = ""
    li = Limestart(password, user_name)
    login_info = li.login()
    username = login_info["username"]
    token = login_info["token"]
    # # 上传记录工具
    # t = ToolsLimeStart(token=token, user_name=username)
    # parser = argparse.ArgumentParser()
    # parser.add_argument('-i', "--input", dest='input', help='input', required=True, nargs='+')
    # args = parser.parse_args()
    # urls = args.input
    # print("urls",urls)
    # for url in urls:
    #     await t.recode_url(url)

    # 获取最新记录工具
    t = ToolsLimeStart(token=token, user_name=username)
    await t.get_url()

    # # 删除记录工具
    # t = ToolsLimeStart(token=token, user_name=username)
    # await t.clear()


if __name__ == '__main__':
    asyncio.run(main())
