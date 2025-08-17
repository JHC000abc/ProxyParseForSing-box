# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@author: JHC000abc@gmail.com
@file: parse_node_snakem982.py
@time: 2025/8/17 15:28 
@desc: 

"""
from urllib import parse
from base_build_json import BuildJson


class ParseNodeSnakem982(BuildJson):
    def __init__(self,port=10809):
        super().__init__(port)

    def process(self):
        """

        :return:
        """

        url = "https://raw.githubusercontent.com/snakem982/proxypool/main/source/v2ray-2.txt"
        for node in self.base64_decode(self.get_html(url).text):
            proxy_url = parse.urlparse(parse.unquote(node))
            self.check_scheme(proxy_url)
