# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@author: JHC000abc@gmail.com
@file: base_build_json.py
@time: 2025/8/17 15:07 
@desc: 

"""
import json
from abc import ABC, abstractmethod
from curl_cffi import requests
import requests
from base64 import b64decode


class BuildJson(ABC):
    """

    """

    def __init__(self, port=10809):
        super().__init__()
        self.port = port
        self.un_used_list = self.get_un_used_list()
        self.tags = []
        self.tags_american = []
        self.outbounds = []

        self.scheme_map = {
            "trojan": self.build_trojan,
            "hysteria2": self.build_hysteria2,
            "vless": self.build_vless,
            "vmess": self.build_vmess,
            "ss": self.build_ss,
        }
        self.proxies = {
            "http": "http://172.17.0.1:10808",
            "https": "http://172.17.0.1:10808"
        }
        # self.proxies = None

    def get_un_used_list(self, file="un_used_proxy.list"):
        """

        :param file:
        :return:
        """
        lis = []
        with open(file, "r", encoding="utf-8") as f:
            for i in f:
                line = i.strip()
                if line:
                    lis.append(line)
        return lis

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

    def forbidden_rules(self, fragment):
        """

        :param fragment:
        :return:
        """
        forbidden_list = ["香港", "台湾", "中国"]
        if any(i for i in forbidden_list if i in fragment):
            return False
        return True

    def parse_proxy_url_ss(self, proxy_url):
        """

        :param proxy_url:
        :return:
        """
        netloc = proxy_url.netloc
        fragment = proxy_url.fragment
        q_map = {"fragment": fragment}
        try:
            for node in self.base64_decode(netloc):
                method, other, server_port = node.split(":")
                password, server = other.split("@")
                q_map["method"] = method
                q_map["server_port"] = int(server_port)
                q_map["server"] = server
                q_map["password"] = password
        except:
            return

        if server in self.un_used_list:
            return

        if not self.forbidden_rules(fragment):
            return

        self.tags.append(fragment)
        if "美国" in fragment:
            self.tags_american.append(fragment)

        return q_map

    def build_ss(self, data):
        """

        :param data:
        :return:
        """
        parse_result = self.parse_proxy_url_ss(data)
        if not parse_result:
            return

        return {
            "type": "shadowsocks",
            "tag": f"{parse_result.get('fragment')}",
            "server": f"{parse_result.get('server')}",
            "server_port": parse_result.get('server_port'),
            "method": f"{parse_result.get('method')}",
            "password": f"{parse_result.get('password')}",
        }

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

        if not self.forbidden_rules(fragment):
            return

        self.tags.append(fragment)
        if "美国" in fragment:
            self.tags_american.append(fragment)

        res = {
            "password": password,
            "ip_port": ip_port,
            "server": server,
            "server_port": int(server_port),
            "fragment": fragment,
        }
        res.update(q_map)
        return res

    def build_vmess(self, data):
        """

        :param data:
        :return:
        """
        parse_result = self.parse_proxy_url_vmess(data)
        if not parse_result:
            return

        return {
            "type": "vmess",
            "tag": f"{parse_result.get('fragment')}",
            "server": f"{parse_result.get('server')}",
            "server_port": parse_result.get('server_port'),
            "uuid": f"{parse_result.get('uuid')}",
            "security": f"{parse_result.get('scy', 'auto')}",
            "tls": {
                "enabled": True,
                "insecure": True,
                "server_name": f"{parse_result.get('sni')}"
            },
            "transport": {
                "type": f"{parse_result.get('type')}",
                "path": f"{parse_result.get('path')}",
                "headers": {
                    "Host": f"{parse_result.get('host')}"
                }
            }
        }

    def parse_proxy_url_vmess(self, proxy_url):
        """

        :param proxy_url:
        :return:
        """
        netloc = proxy_url.netloc

        q_map = {}
        try:
            for node in self.base64_decode(netloc):
                node = json.loads(node)
                server = node["add"]
                fragment = node["ps"]
                server_port = int(node["port"])
                uuid = node["id"]
                type = node["net"]
                path = node.get("path", "/")
                scy = node["scy"]
                host = node.get("host", server)
                sni = host
        except:
            return

        q_map["server"] = server
        q_map["fragment"] = fragment
        q_map["server_port"] = server_port
        q_map["uuid"] = uuid
        q_map["type"] = type
        q_map["path"] = path
        q_map["scy"] = scy
        q_map["host"] = host
        q_map["sni"] = sni

        if server in self.un_used_list:
            return

        if not self.forbidden_rules(fragment):
            return

        if q_map.get('path', "/") == "/":
            return

        self.tags.append(fragment)
        if "美国" in fragment:
            self.tags_american.append(fragment)

        return q_map

    def build_vless(self, data):
        """

        :param data:
        :return:
        """
        parse_result = self.parse_proxy_url_vless(data)
        if not parse_result:
            return
        return {
            "type": "vless",
            "tag": f"{parse_result.get('fragment')}",
            "server": f"{parse_result.get('server')}",
            "server_port": parse_result.get('server_port'),
            "uuid": f"{parse_result.get('uuid')}",
            "tls": {
                "enabled": True,
                "insecure": True,
                "server_name": f"{parse_result.get('sni')}"
            },
            "transport": {
                "type": f"{parse_result.get('type')}",
                "path": f"{parse_result.get('host')}",
                "headers": {
                    "Host": f"{parse_result.get('sni')}"
                }
            }
        }

    def parse_proxy_url_vless(self, data):
        """

        :param data:
        :return:
        """
        type = data.scheme
        netloc = data.netloc
        uuid, other = netloc.split("@")
        server, server_port = other.split(":")
        fragment = data.fragment
        query = data.query.split("&")
        if server in self.un_used_list:
            return

        q_map = {}
        for q in query:
            k, *v = q.split("=")
            q_map[k] = "=".join(v)

        if not self.forbidden_rules(fragment):
            return

        if q_map.get('path', "/") == "/":
            return

        self.tags.append(fragment)
        if "美国" in fragment:
            self.tags_american.append(fragment)

        res = {
            "type": type,
            "uuid": uuid,
            "server": server,
            "server_port": int(server_port),
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
        if parse_result:
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
        if not parse_result:
            return None
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
        else:
            if scheme:
                print(f"发现新协议:{proxy_url}")

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
        response = self.get_html(url, headers=headers)

        contents_url = response.json()["files"][0]["contents_url"]
        response = self.get_html(url=contents_url, headers=headers)
        return response.json()["download_url"]

    @abstractmethod
    def process(self):
        """

        :return:
        """
