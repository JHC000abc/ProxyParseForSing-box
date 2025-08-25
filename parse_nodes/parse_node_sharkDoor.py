# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@author: JHC000abc@gmail.com
@file: parse_node_sharkDoor.py
@time: 2025/8/17 14:33
@desc:

"""
import re
import json
from lxml import etree
from parse_nodes.base import Base
from urllib import parse
from utils.utils_times import UtilsTimes


class ParseNodesharkDoor(Base):
    """

    """

    def __init__(self):
        super().__init__()
        self.search_url = f"https://github.com/sharkDoor/vpn-free-nodes/tree/master/node-list/{UtilsTimes.get_format_utc_8('%Y-%m')}"

    async def parse_search(self, html):
        """

        :param html:
        :return:
        """
        res = re.findall('<script type="application/json" data-target="react-app.embeddedData">(.*?)</script>', html)[0]
        for item in json.loads(res)["payload"]["tree"]["items"]:
            yield item

    async def parse_detail(self, html):
        """

        :param html:
        :return:
        """
        res = re.findall('<script type="application/json" data-target="react-app.embeddedData">(.*?)</script>', html)
        res = res[0]
        data = json.loads(res)["payload"]["blob"]["richText"]
        tree = etree.HTML(data)
        lis = tree.xpath("//tr/td[last()]//text()")
        for li in lis:
            yield li

    async def process(self):
        """

        :return:
        """
        try:
            search_html = await self.fetch_url_get(url=self.search_url, headers=self.headers, proxy=True)
        except:
            return self.success_list
        async for search_result in self.parse_search(search_html):
            day = f"{UtilsTimes.get_format_utc_8('%d')}日"
            name = search_result["name"]
            if not name.startswith(day):
                continue
            detail_url = f'{self.search_url}/{name}'
            try:
                detail_html = await self.fetch_url_get(url=detail_url, headers=self.headers, proxy=True)

                async for node in self.parse_detail(detail_html):
                    node = parse.urlparse(parse.unquote(node.strip()))
                    node_parse_result = await self.build(node)
                    self.success_list.append(node_parse_result)
            except:
                pass
        return self.success_list
