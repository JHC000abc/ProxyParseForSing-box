import asyncio
import os
import re
import traceback
from abc import ABC, abstractmethod
from utils.utils_test_speed import TestSpeed
from parse_schem import *
from utils.utils_encrypt import AsyncEncrypt
from utils.utils_cmd import AsyncCMD
from utils.utils_times import UtilsTimes
from settings.setting import OUT_LISTEN_PORT, UPLOAD_TOOLS_FILE, TELEGRAM_TOOLS_FILE, SPEED_LIMIT, \
    TRANS_PHONE_TOOLS_FILE, LIMESTART_TOOLS_FILE, UPDATE_NODES_TIMES, NODE_TEST_CONNECT_SPEED
from utils.utils_network import UtilsNetwork


class Base(ABC):
    """

    """

    def __init__(self):
        self.net = UtilsNetwork()
        self.headers = {
            "DNT": "1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "sec-ch-ua": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Google Chrome\";v=\"138\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Linux\""
        }
        self.scheme_map = {
            "trojan": ParseTrojan().build_trojan,
            "hysteria2": ParseHysteria2().build_hysteria2,
            "vless": ParseVless().build_vless,
            "vmess": ParseVmess().build_vmess,
            "ss": ParseShadowSocks().build_shadowsocks,
        }
        self.encrypt = AsyncEncrypt()
        self.cmd = AsyncCMD()
        self.port = OUT_LISTEN_PORT
        self.test_speed = TestSpeed()
        self.success_map = {}
        self.success_list = []

    async def build(self, parse_result):
        """

        :param parse_result:
        :return:
        """
        scheme = parse_result.scheme
        if scheme in self.scheme_map:
            try:
                return await self.scheme_map.get(scheme)(parse_result)
            except Exception as e:
                print("解析协议异常", traceback.format_exc())
        else:
            print(f"发现新协议:{scheme}")

    async def get_dns(self):
        """

        :return:
        """
        return {
            "servers": [
                {
                    "tag": "dns_domestic",
                    "address": "223.5.5.5",
                    "address_strategy": "ipv4_only"
                },
                {
                    "tag": "dns_foreign",
                    "address": "8.8.8.8",
                    "address_strategy": "prefer_ipv4"
                }
            ],
            "rules": [
                {
                    "geosite": "cn",
                    "server": "dns_domestic"
                },
                {
                    "outbound": "any",
                    "server": "dns_foreign"
                }
            ]
        }

    async def get_outbounds(self, tags=None, tags_speed=None):
        """

        :param tags:
        :param tags_speed:
        :return:
        """
        return [
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
                "outbounds": ["AUTO-US", "direct-out", "block-out"] + tags,
                "default": "AUTO-US"
            },
            {
                "type": "urltest",
                "tag": "AUTO-US",
                "outbounds": tags_speed,
                "url": f"{NODE_TEST_CONNECT_SPEED}",
                "interval": f"{UPDATE_NODES_TIMES}"
            }

        ]

    async def get_route(self):
        """

        :return:
        """
        return {
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
                    "geosite": "cn",
                    "outbound": "direct-out"
                },
                {
                    "inbound": [
                        "mixed-in"
                    ],
                    "geoip": "cn",
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

    async def get_inbounds(self):
        """

        :return:
        """
        return [
            {
                "type": "mixed",
                "tag": "mixed-in",
                "listen": "::",
                "listen_port": self.port,
                "sniff": True
            }
        ]

    async def parse_node_base64(self, data):
        """

        :param data:
        :return:
        """
        base64_decode_result = await self.encrypt.base64_decode(data.split("# ")[0])
        for node in base64_decode_result.split("\n"):
            if node.strip() and not node.startswith("#"):
                try:
                    yield parse.urlparse(parse.unquote(node.strip()))
                except Exception as e:
                    print(traceback.format_exc())

    async def save_result_json(self, tags, outbounds, tags_speed,
                               file_name=f"config_{UtilsTimes.get_format_utc_8('%Y%m%d%H%M%S')}.json"):
        """

        :param tags:
        :param outbounds:
        :param tags_speed:
        :param file_name:
        :return:
        """
        config_result = {
            "inbounds": await self.get_inbounds(),
            "outbounds": await self.get_outbounds(tags, tags_speed) + outbounds,
            "route": await self.get_route(),
            "dns": await self.get_dns()
        }

        folder = "./configs"
        os.makedirs(folder, exist_ok=True)
        file = os.path.abspath(os.path.join(folder, file_name))
        with open(file, "w", encoding="utf-8") as f:
            f.write(json.dumps(config_result, indent=4, ensure_ascii=False))
        node_nums = len(outbounds)
        print(f"成功将 {node_nums} 个节点保存到:{file}")
        await self.get_cdn_url_by_bos(file, node_nums)

    async def get_cdn_url(self, user_name="JHC000abc", warehouse="ProxyParseForSing-box"):
        """
        这里目前只支持向我自己的github仓库提交后生成CDN 如向自己仓库提交修改 user_name 和warehouse 成自己的即可
        :param user_name:
        :param warehouse:
        :return:
        """
        headers = {
            "referer": "https://www.jsdelivr.com/",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
        }

        url = f"https://api.github.com/repos/{user_name}/{warehouse}/commits/master"
        response = await self.net.fetch_url_get(url, headers=headers)

        contents_url = json.loads(response)["files"][0]["contents_url"]
        response = await self.net.fetch_url_get(url=contents_url, headers=headers)
        return json.loads(response)["download_url"]

    async def get_cdn_url_by_bos(self, file, node_nums):
        """

        :param file:
        :param node_nums:
        :return:
        """
        if node_nums <= 0:
            return
        filename = file.split(os.sep)[-1]
        url = f"https://JHC000abc.github.io/ProxyParseForSing-box/configs/{filename}"
        print("url", url)
        cmd2 = f"{TELEGRAM_TOOLS_FILE} -m '本次成功解析延迟小于{SPEED_LIMIT}ms的节点数量:{node_nums}' '{url}' "
        cmd4 = f"{TRANS_PHONE_TOOLS_FILE} -i {file}"
        cmd5 = f"{LIMESTART_TOOLS_FILE} -i {url}"
        async for msg, proc in self.cmd.run_cmd_async(cmd2):
            print("msg2", msg)
        async for msg, proc in self.cmd.run_cmd_async(cmd4):
            print("msg4", msg)
        async for msg, proc in self.cmd.run_cmd_async(cmd5):
            print("cmd5", msg)

        # cmd = f"{UPLOAD_TOOLS_FILE} -i {file}"
        # async for msg, proc in self.cmd.run_cmd_async(cmd):
        #     print("msg", msg)
        #     match = re.match("https://(.*?).json", msg)
        #     if match:
        #         url = f"https://{match.group(1)}.json"
        #         print("url", url)
        #         cmd2 = f"{TELEGRAM_TOOLS_FILE} -m '本次成功解析延迟小于{SPEED_LIMIT}ms的节点数量:{node_nums}' '{url}' "
        #         cmd4 = f"{TRANS_PHONE_TOOLS_FILE} -i {file}"
        #         cmd5 = f"{LIMESTART_TOOLS_FILE} -i {url}"
        #         async for msg, proc in self.cmd.run_cmd_async(cmd2):
        #             print("msg2", msg)
        #         async for msg, proc in self.cmd.run_cmd_async(cmd4):
        #             print("msg4", msg)
        #         async for msg, proc in self.cmd.run_cmd_async(cmd5):
        #             print("cmd5", msg)

    async def get_data_from_github(self, url):
        """

        从 github 页面接口获取数据 readme 接口
        :return:
        """
        headers = {
            "accept": "application/json",
            "accept-language": "zh,zh-CN;q=0.9",
            "content-type": "application/json",
            "referer": "https://github.com/Barabama/FreeNodes?tab=readme-ov-file",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        }
        return await self.net.fetch_url_get(url, headers=headers, proxy=True)

    @abstractmethod
    async def process(self, *args, **kwargs):
        """

        :return:
        """
