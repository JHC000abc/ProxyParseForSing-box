# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@author: JHC000abc@gmail.com
@file: parse_node_snakem982.py
@time: 2025/8/17 15:28 
@desc: 

"""
import json
import re
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
            },
            {
                "url": "https://raw.githubusercontent.com/AliDev-ir/FreeVPN/main/pcvpn",
                "proxy": True
            },

            {
                "url": "https://raw.githubusercontent.com/penhandev/AutoAiVPN/refs/heads/main/allConfigs.txt",
                "proxy": True
            },
            {
                "url": "https://raw.githubusercontent.com/crackbest/V2ray-Config/refs/heads/main/config.txt",
                "proxy": True
            },
            {
                "url":"https://github.com/kismetpro/NodeSuber/raw/refs/heads/main/out/All_Configs_Sub.txt",
                 "proxy": True
            },

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

    async def parse_node_free_proxy_nodes(self, data):
        """

        :param data:
        :return:
        """
        data = json.loads(data)
        richText = data["payload"]["tree"]["readme"]["richText"]

        res = re.findall('# V2ray订阅链接：(.*?)</code></pre></div>', richText,re.DOTALL)
        if res:
            for i in res:
                for url in [i for i in i.split("\n") if i]:
                    self.infos.extend([{
                        "url": url,
                        "proxy": True
                    }])


    async def get_expire_node(self):
        """

        :return:
        """
        return """"""

    async def process(self):
        """

        :return:
        """
        git_hub_pages_urls = {
            "https://github.com/Barabama/FreeNodes/overview-files/main": self.parse_node_Barabama,
            "https://github.com/vpnmianfei/vpnmianfei.github.io/overview-files/main": self.parse_node_vpnmianfei,
            # "https://github.com/free-proxy-nodes/free-nodes": self.parse_node_free_proxy_nodes,
            # "https://github.com/barry-far/V2ray-Config/overview-files/main": self.parse_node_barry_far
        }
        for url, func in git_hub_pages_urls.items():
            data = await self.get_data_from_github(url)
            await func(data)

        index = 0
        for info in self.infos:
            url = info["url"]
            proxy = info["proxy"]
            try:
                res = await self.net.fetch_url_get(url, headers=self.headers, proxy=proxy)
                if index == 0:
                    expire_nodes = await self.get_expire_node()
                    res += expire_nodes
                    print(f"加载过期订阅:{expire_nodes}")
                async for node in self.parse_node_base64(res):
                    try:
                        node_parse_result = await self.build(node)
                        if node_parse_result:
                            self.success_list.append(node_parse_result)
                    except:
                        print(f"ParseNodeSnakem982 节点解析错误：{node}")
            except  Exception as e:
                print(f"ParseNodeSnakem982:{traceback.format_exc()}")
            index += 1
        return self.success_list


async def main():
    p2 = ParseNodeSnakem982()
    await p2.process()


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())
