# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@author: JHC000abc@gmail.com
@file: gen_latest_CDN.py
@time: 2025/8/17 16:11 
@desc: 

"""
import asyncio
from base import Base


class GetLatestCDN(Base):
    def __init__(self):
        super().__init__()

    async def process(self):
        """

        :return:
        """
        print("仓库中最新上传的文件CDN:", await self.get_cdn_url())


async def main():
    """

    :return:
    """
    cdn = GetLatestCDN()
    await cdn.process()

if __name__ == '__main__':
    asyncio.run(main())
