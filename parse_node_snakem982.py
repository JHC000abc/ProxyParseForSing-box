# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@author: JHC000abc@gmail.com
@file: parse_node_snakem982.py
@time: 2025/8/17 15:28 
@desc: 

"""
from base import Base


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
            res = await self.fetch_url_get(url, headers=self.headers, proxy=proxy)
            async for node in self.parse_node_base64(res):
                node_parse_result = await self.build(node)
                if node_parse_result:
                    self.success_list.append(node_parse_result)
        return self.success_list
        #             status, res = await self.test_speed.test_speed(node_parse_result)
        #             if status:
        #                 print("测速成功")
        #                 self.success_map.update(res)
        #             else:
        #                 print("测速失败")
        #     print(f"{self.__class__.__name__} {url} 中解析到可用节点:{len(self.success_map)}")
        #
        # return self.success_map
