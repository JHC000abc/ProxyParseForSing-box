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
from settings import UPLOAD_TOOLS_FILE, TELEGRAM_TOOLS_FILE


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
                    "listen_port": 1080,
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
                                     "SELECT-US",
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
                    "url": "https://gemini.google.com/gem",
                    "interval": "1m"
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
        tmp_file = "tmp.json"
        with open(tmp_file, "w", encoding="utf-8") as f:
            json.dump(main_json, f, ensure_ascii=False, indent=4)

        cmd = f"{UPLOAD_TOOLS_FILE} -i {tmp_file}"
        async for msg, proc in self.cmd.run_cmd_async(cmd):
            print("msg", msg)
            match = re.match("https://(.*?).json", msg)
            if match:
                url = f"https://{match.group(1)}.json"
                cmd2 = f"{TELEGRAM_TOOLS_FILE} -m '生成手机专用订阅链接' "
                cmd3 = f"{TELEGRAM_TOOLS_FILE} -m '{url}'"
                async for msg, proc in self.cmd.run_cmd_async(cmd2):
                    print("msg2", msg)
                async for msg, proc in self.cmd.run_cmd_async(cmd3):
                    print("msg3", msg)

        os.remove(tmp_file)


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
