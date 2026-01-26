# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@author: JHC000abc@gmail.com
@file: tools_trans_phone.py
@time: 2025/8/25 21:19 
@desc: 

"""
import argparse
import asyncio
import json
import os
import re
from utils.utils_cmd import AsyncCMD
from utils.utils_times import UtilsTimes

from settings.setting import UPLOAD_TOOLS_FILE, TELEGRAM_TOOLS_FILE, OUT_LISTEN_PORT, UPDATE_NODES_TIMES, \
    NODE_TEST_CONNECT_SPEED


class AsyncToolsTransPhone:
    """

    """

    def __init__(self):
        self.cmd = AsyncCMD()

    async def build_main_json(self, tags, out_bounds):
        """

        :param tags:
        :param out_bounds:
        :return:
        """
        main_json = {
            "inbounds": [
                {
                    "type": "mixed",
                    "tag": "mixed-in",
                    "listen": "::",
                    "listen_port": OUT_LISTEN_PORT,
                    "sniff": True
                }
            ],
            "outbounds": [
                {
                    "type": "direct",
                    "tag": "direct-out"
                },
                {
                    "type": "block",
                    "tag": "block-out"
                },
                {
                    "type": "selector",
                    "tag": "PROXY",
                    "outbounds": [
                                     "AUTO-US",
                                     "direct-out",
                                     "block-out"
                                 ] + tags,
                    "default": "AUTO-US"
                },
                {
                    "type": "selector",
                    "tag": "SELECT-US",
                    "outbounds": tags

                },
                {
                    "type": "urltest",
                    "tag": "AUTO-US",
                    "outbounds": tags,
                    "url": f"{NODE_TEST_CONNECT_SPEED}",
                    "interval": f"{UPDATE_NODES_TIMES}"
                }

            ],
            "route": {
                "rules": [
                    {
                        "inbound": [
                            "mixed-in"
                        ],
                        "ip_is_private": True,
                        "outbound": "direct-out"
                    },
                    {
                        "inbound": [
                            "mixed-in"
                        ],
                        "outbound": "PROXY"
                    }
                ]
            }
        }

        main_json["outbounds"].extend(out_bounds)
        return main_json

    async def read_origin(self, file):
        """

        :param file:
        :return:
        """
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data

    async def parse_data(self, data: dict):
        """

        :param data:
        :return:
        """
        schema_set = {
            "vless", "vmess", "trojan", "hysteria2", "ss"
        }
        res = []
        tags = []
        node_nums = 0
        outbounds = data["outbounds"]
        for outbound in outbounds:
            schema = outbound["type"]
            if schema in schema_set:
                res.append(outbound)
                tags.append(outbound["tag"])
                node_nums += 1
        return tags, res, node_nums

    async def process(self, file):
        """

        :param file:
        :return:
        """
        data = await self.read_origin(file)
        tags, outbounds, node_nums = await self.parse_data(data)
        if node_nums <= 0:
            return
        main_json = await self.build_main_json(tags, outbounds)
        filename = f"phone_{UtilsTimes.get_format_utc_8('%Y%m%d')}.json"
        folder = "./configs"
        os.makedirs(folder, exist_ok=True)
        tmp_file = os.path.abspath(os.path.join(folder, filename))
        with open(tmp_file, "w", encoding="utf-8") as f:
            json.dump(main_json, f, ensure_ascii=False, indent=4)

        url = f"https://JHC000abc.github.io/ProxyParseForSing-box/{filename}"
        cmd2 = f"{TELEGRAM_TOOLS_FILE} -m '生成手机专用订阅链接' '{url}' "
        async for msg, proc in self.cmd.run_cmd_async(cmd2):
            print("msg2", msg)

        # cmd = f"{UPLOAD_TOOLS_FILE} -i {tmp_file}"
        # async for msg, proc in self.cmd.run_cmd_async(cmd):
        #     print("msg", msg)
        #     match = re.match("https://(.*?).json", msg)
        #     if match:
        #         url = f"https://{match.group(1)}.json"
        #         cmd2 = f"{TELEGRAM_TOOLS_FILE} -m '生成手机专用订阅链接' '{url}' "
        #         async for msg, proc in self.cmd.run_cmd_async(cmd2):
        #             print("msg2", msg)

        # os.remove(tmp_file)


async def main():
    """

    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', "--file", dest='file', help='file', required=True, nargs='+')
    args = parser.parse_args()
    for file in args.file:
        await AsyncToolsTransPhone().process(file)


if __name__ == '__main__':
    asyncio.run(main())
