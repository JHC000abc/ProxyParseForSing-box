# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@author: JHC000abc@gmail.com
@file: parse_node_snakem982.py
@time: 2025/8/17 15:28 
@desc: 

"""
import json
import traceback
from lxml import etree
from parse_nodes.base import Base


class ParseNodeSnakem982(Base):
    """

    """

    def __init__(self):
        super().__init__()
        self.infos = [
            {
                "url": "https://raw.githubusercontent.com/snakem982/proxypool/main/source/v2ray-2.txt",
                "proxy": True
            },
            {

                "url": "https://a.nodeshare.xyz/uploads/2025/7/20250720.txt",
                "proxy": True
            },
            {
                "url": "https://raw.githubusercontent.com/shaoyouvip/free/refs/heads/main/base64.txt",
                "proxy": True
            }
            # ,
            # {
            #     "url": "https://raw.githubusercontent.com/penhandev/AutoAiVPN/refs/heads/main/allConfigs.txt",
            #     "proxy": True
            # },
            # {
            #     "url": "https://raw.githubusercontent.com/crackbest/V2ray-Config/refs/heads/main/config.txt",
            #     "proxy": True
            # },
            # {
            #     "url": "https://raw.githubusercontent.com/AliDev-ir/FreeVPN/main/pcvpn",
            #     "proxy": True
            # },

        ]

    async def build_tree(self, atticles):
        """

        :param atticles:
        :return:
        """
        html_base = f"""<!DOCTYPE html>
                        <html lang="en">
                        <head>
                            <meta charset="UTF-8">
                            <title>Title</title>
                            {atticles}

                        </head>
                        <body>

                        </body>
                        </html>"""

        return etree.HTML(html_base)

    async def parse_node_vpnmianfei(self, data):
        """

        :param data:
        :return:
        """
        rule = '//article/ul[2][@dir="auto"]/li/a/@href'
        atticles = json.loads(data)["files"][0]["richText"]
        tree = await self.build_tree(atticles)
        lis = tree.xpath(rule)
        for url in lis:
            self.infos.extend([{
                "url": url,
                "proxy": True
            }])

    async def parse_node_Barabama(self, data):
        """

        :param data:
        :return:
        """
        rule = '//tbody/tr/td[2]/a[1]/@href'
        atticles = json.loads(data)["files"][0]["richText"]
        tree = await self.build_tree(atticles)
        lis = tree.xpath(rule)
        for url in lis:
            self.infos.extend([{
                "url": url,
                "proxy": True
            }])

    async def parse_node_barry_far(self, data):
        """

        :param data:
        :return:
        """
        rule = '//article/p[position()>=25 and position()<= 28]/a/@href'
        atticles = json.loads(data)["files"][0]["richText"]
        tree = await self.build_tree(atticles)
        lis = tree.xpath(rule)
        for url in lis:
            self.infos.extend([{
                "url": url,
                "proxy": True
            }])

    async def process(self):
        """

        :return:
        """
        git_hub_pages_urls = {
            "https://github.com/Barabama/FreeNodes/overview-files/main": self.parse_node_Barabama,
            "https://github.com/vpnmianfei/vpnmianfei.github.io/overview-files/main": self.parse_node_vpnmianfei,
            # "https://github.com/barry-far/V2ray-Config/overview-files/main": self.parse_node_barry_far
        }
        for url, func in git_hub_pages_urls.items():
            data = await self.get_data_from_github(url)
            await func(data)

        for info in self.infos:
            url = info["url"]
            proxy = info["proxy"]
            try:
                res = await self.net.fetch_url_get(url, headers=self.headers, proxy=proxy)
                async for node in self.parse_node_base64(res):
                    node_parse_result = await self.build(node)
                    if node_parse_result:
                        self.success_list.append(node_parse_result)
            except  Exception as e:
                print(f"ParseNodeSnakem982:{traceback.format_exc()}")
        return self.success_list
