# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@author: JHC000abc@gmail.com
@file: parse_node_snakem982.py
@time: 2025/8/17 15:28 
@desc: 

"""
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
                "proxy": False
            }
        ]

    async def process(self):
        """

        :return:
        """
        for info in self.infos:
            url = info["url"]
            proxy = info["proxy"]
            try:
                res = await self.fetch_url_get(url, headers=self.headers, proxy=proxy)
                async for node in self.parse_node_base64(res):
                    node_parse_result = await self.build(node)
                    if node_parse_result:
                        self.success_list.append(node_parse_result)
            except:
                pass
        return self.success_list
