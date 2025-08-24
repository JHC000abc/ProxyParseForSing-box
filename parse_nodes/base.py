import os
import re
from abc import ABC, abstractmethod
from datetime import datetime
import aiohttp
from settings import PROXIES_ASYNC, OUT_LISTEN_PORT, UPLOAD_TOOLS_FILE
from utils.utils_test_speed import TestSpeed
from parse_schem import *
from utils.utils_retry import retry
from utils.utils_encrypt import AsyncEncrypt
from utils.utils_cmd import AsyncCMD


class Base(ABC):
    """

    """

    def __init__(self):
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
            return await self.scheme_map.get(scheme)(parse_result)
        else:
            print(f"发现新协议:{scheme}")

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
                "outbounds": ["AUTO-US", "SELECT-US", "direct-out", "block-out"] + tags,
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
                "outbounds": tags_speed,
                "url": "https://gemini.google.com/gem",
                "interval": "1m"
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

    @retry
    async def fetch_url_get(self, url, headers=None, cookies=None, proxy=None):
        """

        :param url:
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
            async with session.get(url, proxy=proxy, headers=headers, cookies=cookies) as response:
                response.raise_for_status()
                html_content = await response.text()
                return html_content

    async def parse_node_base64(self, data):
        """

        :param data:
        :return:
        """
        base64_decode_result = await self.encrypt.base64_decode(data)
        for node in base64_decode_result.split("\n"):
            if node.strip():
                yield parse.urlparse(parse.unquote(node.strip()))

    async def save_result_json(self, tags, outbounds, tags_speed,
                               file_name=f"config_{datetime.now().strftime('%Y%m%d')}.json"):
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
            "route": await self.get_route()
        }

        folder = "./configs"
        os.makedirs(folder, exist_ok=True)
        file = os.path.abspath(os.path.join(folder, file_name))
        with open(file, "w", encoding="utf-8") as f:
            f.write(json.dumps(config_result, indent=4, ensure_ascii=False))

        print(f"成功将 {len(outbounds)} 个节点保存到:{file}")
        await self.get_cdn_url_by_bos(file)

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
        response = await self.fetch_url_get(url, headers=headers)

        contents_url = json.loads(response)["files"][0]["contents_url"]
        response = await self.fetch_url_get(url=contents_url, headers=headers)
        return json.loads(response)["download_url"]

    async def get_cdn_url_by_bos(self, file):
        """

        :param file:
        :return:
        """
        cmd = f"{UPLOAD_TOOLS_FILE} -i {file}"

        async for msg, proc in self.cmd.run_cmd_async(cmd):
            match = re.match("https://(.*?).json", msg)
            if match:
                url = f"https://{match.group(1)}.json"
                print(f" [CDN] :{url}")

        os.system(cmd)

    @abstractmethod
    async def process(self):
        """

        :return:
        """
