# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@author: JHC000abc@gmail.com
@file: base_build_json.py
@time: 2025/8/17 15:07 
@desc: 

"""
from abc import ABC, abstractmethod
from curl_cffi import requests
from base64 import b64decode


class BuildJson(ABC):
    """

    """

    def __init__(self, port=10809):
        super().__init__()
        self.port = port
        self.un_used_list = []
        self.tags = []
        self.tags_american = []
        self.outbounds = []

        self.scheme_map = {
            "trojan": self.build_trojan,
            "hysteria2": self.build_hysteria2,
        }
        self.proxies = {
            "http": "http://172.17.0.1:10808",
            "https": "http://172.17.0.1:10808"
        }

    def get_outbounds(self):
        """

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
                "outbounds": ["AUTO-US", "SELECT-US", "direct-out", "block-out"] + self.tags,
                "default": "AUTO-US"
            },
            {
                "type": "selector",
                "tag": "SELECT-US",
                "outbounds": self.tags_american

            },
            {
                "type": "urltest",
                "tag": "AUTO-US",
                "outbounds": self.tags,
                # "url": "https://gemini.google.com/app",
                "url": "https://gemini.google.com/gem",
                "interval": "1m"
            },

        ]

    def get_route(self):
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
                    "outbound": "PROXY"
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
                }
            ]
        }

    def get_inbounds(self):
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

    def parse_proxy_url(self, proxy_url):
        """

        :param proxy_url:
        :return:
        """
        password, ip_port = proxy_url.netloc.split("@")
        server, server_port = ip_port.split(":")
        server_port = server_port.split(",")[0]
        query = proxy_url.query.split("&")

        if server in self.un_used_list:
            return

        q_map = {}
        for q in query:
            k, *v = q.split("=")

            q_map[k] = "=".join(v)
        fragment = proxy_url.fragment

        self.tags.append(fragment)

        if "美国" in fragment:
            self.tags_american.append(fragment)
        res = {
            "password": password,
            "ip_port": ip_port,
            "server": server,
            "server_port": int(server_port),
            "q_map": q_map,
            "fragment": fragment,
        }
        res.update(q_map)
        return res

    def build_trojan(self, data):
        """

        :param data:
        :return:
        """
        parse_result = self.parse_proxy_url(data)
        return {
            "type": "trojan",
            "tag": parse_result.get("fragment"),
            "server": parse_result.get("server"),
            "server_port": parse_result.get("server_port"),
            "password": parse_result.get("password"),
            "tls": {
                "enabled": True,
                "insecure": True,
                "server_name": parse_result.get("sni")
            }
        }

    def build_hysteria2(self, data):
        """

        :param data:
        :return:
        """
        parse_result = self.parse_proxy_url(data)
        return {
            "type": "hysteria2",
            "tag": parse_result.get("fragment"),
            "server": parse_result.get("server"),
            "server_port": parse_result.get("server_port"),
            "password": parse_result.get("password"),
            "tls": {
                "enabled": True,
                "insecure": True,
                "server_name": parse_result.get("sni")
            }
        }

    def check_scheme(self, proxy_url):
        """

        :param proxy_url:
        :return:
        """
        scheme = proxy_url.scheme
        if scheme in self.scheme_map.keys():
            outbound = self.scheme_map.get(scheme)(proxy_url)
            if outbound:
                self.outbounds.append(outbound)

    def get_html(self, url, headers=None, cookies=None):
        """

        :param url:
        :return:
        """
        response = requests.get(url, proxies=self.proxies, headers=headers, cookies=cookies)
        if response.status_code != 200:
            raise ValueError("获取节点数据失败")
        return response

    def base64_decode(self, data):
        """

        :param data:
        :return:
        """
        for node in b64decode(data).decode("utf-8").split("\n"):
            yield node

    def get_download_url(self, user_name="JHC000abc", warehouse="ProxyParseForSing-box"):
        """

        """
        headers = {
            "referer": "https://www.jsdelivr.com/",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
        }

        url = f"https://api.github.com/repos/{user_name}/{warehouse}/commits/master"
        response = self.get_html(url, headers=headers)

        contents_url = response.json()["files"][0]["contents_url"]
        response = self.get_html(url=contents_url, headers=headers)
        return response.json()["download_url"]

    @abstractmethod
    def process(self):
        """

        :return:
        """
