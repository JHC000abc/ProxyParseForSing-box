# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@author: JHC000abc@gmail.com
@file: utils_network.py
@time: 2025/8/26 18:45 
@desc: 

"""
import aiohttp
from utils.utils_retry import retry
from settings.setting import PROXIES_ASYNC, TIMEOUT


class UtilsNetwork:
    """

    """

    @retry
    async def fetch_url_get(self, url, params=None, headers=None, cookies=None, proxy=None):
        """

        :param url:
        :param params:
        :param headers:
        :param cookies:
        :param proxy:
        :return:
        """
        if proxy:
            proxy = PROXIES_ASYNC
        else:
            proxy = None
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)
                                         ) as session:
            async with session.get(url, params=params, proxy=proxy, headers=headers, cookies=cookies,
                                   timeout=TIMEOUT) as response:
                response.raise_for_status()
                html_content = await response.text()
                return html_content

    @retry
    async def fetch_url_post(self, url, headers=None, cookies=None, proxy=None, data=None):
        """

        :param url:
        :param headers:
        :param cookies:
        :param proxy:
        :param data:
        :return:
        """
        if proxy:
            proxy = PROXIES_ASYNC
        else:
            proxy = None
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)
                                         ) as session:
            async with session.post(url, proxy=proxy, headers=headers, cookies=cookies, json=data,
                                    timeout=TIMEOUT) as response:
                response.raise_for_status()
                html_content = await response.text()
                return html_content

    @retry
    async def fetch_url_delete(self, url, params=None, headers=None, cookies=None, proxy=None):
        """

        :param url:
        :param params:
        :param headers:
        :param cookies:
        :param proxy:
        :return:
        """
        if proxy:
            proxy = PROXIES_ASYNC
        else:
            proxy = None
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)
                                         ) as session:
            async with session.delete(url, params=params, proxy=proxy, headers=headers, cookies=cookies,
                                      timeout=TIMEOUT) as response:
                response.raise_for_status()
                html_content = await response.text()
                return html_content
