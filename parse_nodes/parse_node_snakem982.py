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
            },
            {
                "url": "https://raw.githubusercontent.com/AliDev-ir/FreeVPN/main/pcvpn",
                "proxy": True
            },

            # {
            #     "url": "https://raw.githubusercontent.com/penhandev/AutoAiVPN/refs/heads/main/allConfigs.txt",
            #     "proxy": True
            # },
            # {
            #     "url": "https://raw.githubusercontent.com/crackbest/V2ray-Config/refs/heads/main/config.txt",
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

    async def get_expire_node(self):
        """

        :return:
        """
        return """trojan://xaLw4aO6Dw@50.115.173.177:21043?allowInsecure=1&peer=v.qq.com&sni=v.qq.com#%E6%B6%88%E6%81%AF%3A%202%E6%9D%A1%E6%9C%AA%E8%AF%BB%EF%BC%8C%E5%9C%A8APP%E6%9F%A5%E7%9C%8B
trojan://xaLw4aO6Dw@50.115.173.177:21043?allowInsecure=1&peer=v.qq.com&sni=v.qq.com#%E7%BE%8E%E5%9B%BD%20G1%20%7C%20%E7%9B%B4%E8%BF%9E%E3%80%81%E7%A7%BB%E5%8A%A8%E4%BC%98%E5%8C%96%20%7C%203x
trojan://xaLw4aO6Dw@23.142.200.97:48369?allowInsecure=1&peer=v.qq.com&sni=v.qq.com#%E7%BE%8E%E5%9B%BD%20G2%20%7C%20%E7%9B%B4%E8%BF%9E%E3%80%81ChatGPT%20%7C%203x
trojan://xaLw4aO6Dw@89.185.80.174:48240?allowInsecure=1&peer=v.qq.com&sni=v.qq.com#%E7%BE%8E%E5%9B%BD%20G4%20%7C%20%E7%9B%B4%E8%BF%9E%20%7C%203x
trojan://xaLw4aO6Dw@211.72.156.82:14571?allowInsecure=1&peer=v.qq.com&sni=v.qq.com#%E9%A6%99%E6%B8%AF%20G1%20%7C%20%E5%B0%8F%E5%B8%A6%E5%AE%BD%20%7C%204x
trojan://xaLw4aO6Dw@50.115.173.177:21043?allowInsecure=1&peer=v.qq.com&sni=v.qq.com#-----%20%E8%B4%A6%E5%8F%B7%E4%BF%A1%E6%81%AF%20-----
trojan://xaLw4aO6Dw@50.115.173.177:21043?allowInsecure=1&peer=v.qq.com&sni=v.qq.com#%E7%99%BB%E5%BD%95%E8%B4%A6%E5%8F%B7%3A%20saijelu%40f.lm%20%20%20%20%20%20%20%20%20%20%20%20%20%20
trojan://xaLw4aO6Dw@50.115.173.177:21043?allowInsecure=1&peer=v.qq.com&sni=v.qq.com#%E4%BD%93%E9%AA%8C%E5%A5%97%E9%A4%90%3A%20%E5%89%A9%E4%BD%992%E5%A4%A9%20%20%20%20%20%20%20%20%20%20%20%20%20%20
trojan://xaLw4aO6Dw@50.115.173.177:21043?allowInsecure=1&peer=v.qq.com&sni=v.qq.com#%E6%B5%81%E9%87%8F%E9%87%8D%E7%BD%AE%3A%20%E6%AF%8F%E6%9C%882%E6%97%A5%2010G%EF%BC%8C%E5%89%A9%E4%BD%998G%20%20%20%20%20%20%20%20%20%20%20%20%20%20
trojan://xaLw4aO6Dw@50.115.173.177:21043?allowInsecure=1&peer=v.qq.com&sni=v.qq.com#-----%20%E8%81%94%E7%B3%BB%E6%88%91%E4%BB%AC%20-----
trojan://xaLw4aO6Dw@50.115.173.177:21043?allowInsecure=1&peer=v.qq.com&sni=v.qq.com#%E7%94%B5%E6%8A%A5%3A%20https%3A%2F%2Ft.me%2Ffalemon_group
trojan://xaLw4aO6Dw@50.115.173.177:21043?allowInsecure=1&peer=v.qq.com&sni=v.qq.com#%E9%82%AE%E7%AE%B1%3A%20kefu%40falemon.com
trojan://xaLw4aO6Dw@50.115.173.177:21043?allowInsecure=1&peer=v.qq.com&sni=v.qq.com#%E5%AE%98%E7%BD%91%3A%20mp.dtbaq.cn%2Fol
trojan://xaLw4aO6Dw@50.115.173.177:21043?allowInsecure=1&peer=v.qq.com&sni=v.qq.com#%E6%97%B6%E9%97%B4%3A%202025-09-02%2020%3A16%3A48"""

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
