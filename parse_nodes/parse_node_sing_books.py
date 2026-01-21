# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@author: JHC000abc@gmail.com
@file: parse_node_sing_books.py
@time: 2025/12/11 15:37 
@desc: 

"""
import asyncio
import re
import json
import os
from lxml import etree
from parse_nodes.base import Base



class ParseNodeSingBooks(Base):
    """

    """

    def __init__(self):
        super().__init__()
        self.search_url = [
            "https://fastly.jsdelivr.net/gh/Alvin9999/pac2@latest/singbox/config.json",
            "https://gitlab.com/free9999/ipupdate/-/raw/master/singbox/config.json"
        ]

    async def parse_search(self, html):
        """

        :param html:
        :return:
        """
        data = json.loads(html)
        outbounds = data["outbounds"]
        return outbounds

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
        res = {}
        for url in self.search_url:
            try:
                search_html = await self.net.fetch_url_get(url=url, headers=self.headers, proxy=True)
            except Exception as e:
                return self.success_list
            search_result = await self.parse_search(search_html)
            for i in search_result:
                tag = f'{i["tag"]}_{i["server"]}_{i["server_port"]}'
                i["tag"] = tag
                res.update({
                    tag : i
                })
        config_result = {
            "inbounds": await self.get_inbounds(10808),
            "outbounds": await self.get_outbounds(list(res.keys()), list(res.keys()))+list(res.values()),
            "route": await self.get_route(),
            "dns": await self.get_dns()
        }

        folder = "./configs"
        file_name = "config_local.json"
        os.makedirs(folder, exist_ok=True)
        file = os.path.abspath(os.path.join(folder, file_name))
        with open(file, "w", encoding="utf-8") as f:
            f.write(json.dumps(config_result, indent=4, ensure_ascii=False))
        node_nums = len(list(res.values()))
        print(f"成功将 {node_nums} 个节点保存到:{file}")


# async def main():
#     p2 = ParseNodeSingBooks()
#     await p2.process()
#
#
# if __name__ == '__main__':
#     asyncio.run(main())
