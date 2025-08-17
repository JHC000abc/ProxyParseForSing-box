# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@author: JHC000abc@gmail.com
@file: get_latest_CDN.py
@time: 2025/8/17 16:11 
@desc: 

"""

from base_build_json import BuildJson


class GetLatestCDN(BuildJson):
    def __init__(self, port=10809):
        super().__init__(10809)

    def process(self):
        print("仓库中最新上传的文件CDN:", self.get_download_url())


if __name__ == '__main__':
    cdn = GetLatestCDN()
    cdn.process()
