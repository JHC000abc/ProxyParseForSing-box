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
from base_build_json import BuildJson


class ParseNodesharkDoor(BuildJson):
    """

    """

    def __init__(self, port=10809):
        super().__init__(port)
        self.base_url = f"https://github.com/sharkDoor/vpn-free-nodes/tree/master/node-list/"
        self.search_url = f"{self.base_url}{datetime.now().strftime('%Y-%m')}"

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

    def process(self):
        """

        :return:
        """
        search_response = self.get_html(url=self.search_url)
        search_result = self.parse_search(search_response.text)
        detail_url = f'{self.search_url}/{search_result["name"]}'
        detail_response = self.get_html(url=detail_url)
        for node in self.parse_detail(detail_response.text):
            proxy_url = parse.urlparse(parse.unquote(node))
            self.check_scheme(proxy_url)
