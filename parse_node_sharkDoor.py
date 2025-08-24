# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@author: JHC000abc@gmail.com
@file: parse_node_sharkDoor.py
@time: 2025/8/17 14:33
@desc:

"""
from urllib import parse
from datetime import datetime
import re
import json
from lxml import etree
from base import Base


class ParseNodesharkDoor(Base):
    """

    """

    def __init__(self):
        super().__init__()
        self.search_url = f"https://github.com/sharkDoor/vpn-free-nodes/tree/master/node-list/{datetime.now().strftime('%Y-%m')}"

    def parse_search(self, html):
        """

        :param html:
        :return:
        """
        res = re.findall('<script type="application/json" data-target="react-app.embeddedData">(.*?)</script>', html)[0]
        for item in json.loads(res)["payload"]["tree"]["items"]:
            pass
        return item

    def parse_detail(self, html):
        """

        :param html:
        :return:
        """
        res = re.findall('<script type="application/json" data-target="react-app.embeddedData">(.*?)</script>', html)[0]
        data = json.loads(res)["payload"]["blob"]["richText"]
        tree = etree.HTML(data)
        lis = tree.xpath("//tr/td[last()]//text()")
        for li in lis:
            yield li

    async def process(self):
        """

        :return:
        """
        search_html = await self.fetch_url_get(url=self.search_url, headers=self.headers, proxy=True)
        search_result = self.parse_search(search_html)
        detail_url = f'{self.search_url}/{search_result["name"]}'
        detail_html = await self.fetch_url_get(url=detail_url, headers=self.headers, proxy=True)

        for node in self.parse_detail(detail_html):
            node = parse.urlparse(parse.unquote(node.strip()))
            node_parse_result = await self.build(node)
            self.success_list.append(node_parse_result)
        return self.success_list

            # if node_parse_result:
            #     status, res = await self.test_speed.test_speed(node_parse_result)
            #     if status:
            #         print("测速成功")
            #         self.success_map.update(res)
            #     else:
            #         print("测速失败")
        # print(f"{self.__class__.__name__} {detail_url} 中解析到可用节点:{len(self.success_map)}")
        # return self.success_map


