import json
from base64 import b64decode
# import requests
from curl_cffi import requests
from datetime import datetime
from urllib import parse


class ParseBookUrl:
    """

    """

    def __init__(self, url):
        self.url = url
        self.un_used_list = ["108.181.5.132", "108.181.5.130"]
        # ["44.248.19.137", "test.hdcloud.link", "51.158.218.2", "13.115.222.211", "13.231.157.171", "52.63.97.82",
        #  "129.153.52.235", "192.18.150.167"]

    def get_main_json(self):
        """

        """
        return {
            "inbounds": [
                {
                    "type": "mixed",
                    "tag": "mixed-in",
                    "listen": "::",
                    "listen_port": 10808,
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
                                              ] + self.tags,
                                 "default": "AUTO-US"
                             },
                             {
                                 "type": "selector",
                                 "tag": "SELECT-US",
                                 "outbounds": self.tags_arimician

                             },
                             {
                                 "type": "urltest",
                                 "tag": "AUTO-US",
                                 "outbounds": self.tags,
                                 "url": "https://gemini.google.com/app",
                                 "interval": "5m"
                             },

                         ] + self.outbounds,
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
        }

    def get_book_data(self):
        """

        """
        proxies = {
            "http": "http://172.17.0.1:10808",
            "https": "http://172.17.0.1:10808"
        }
        # proxies = None
        response = requests.get(self.url, proxies=proxies)
        if response.status_code != 200:
            raise ValueError("获取节点数据失败")
        return response

    def decode_data(self, data):
        """

        """
        for node in b64decode(data).decode("utf-8").split("\n"):
            if node.strip():
                yield node

    def parse_scheme(self, url_data):
        """

        """
        scheme = url_data.scheme
        scheme_map = {
            "trojan": self.parse_trojan,
            "hysteria2": self.parse_hysteria2,
            "shadowsocks": self.parse_shadowsocks,
        }

        if scheme in scheme_map.keys():
            outbound = scheme_map.get(scheme)(url_data)
            if outbound:
                self.outbounds.append(outbound)

    def parse_shadowsocks(self, data):
        """

        """
        password, ip_port = data.netloc.split("@")
        server, server_port = ip_port.split(":")
        server_port = server_port.split(",")[0]
        query = data.query.split("&")

        if server in self.un_used_list:
            return

        q_map = {}
        for q in query:
            k, *v = q.split("=")

            q_map[k] = "=".join(v)
        fragment = data.fragment

        self.tags.append(fragment)
        if "美国" in fragment:
            self.tags_arimician.append(fragment)
        result = {
            "type": "hysteria2",
            "tag": fragment,
            "server": server,
            "server_port": int(server_port),
            "password": password,
            # "method": method

        }

        return result

    def parse_hysteria2(self, data):
        """

        """
        password, ip_port = data.netloc.split("@")
        server, server_port = ip_port.split(":")
        server_port = server_port.split(",")[0]
        query = data.query.split("&")

        if server in self.un_used_list:
            return

        q_map = {}
        for q in query:
            k, *v = q.split("=")

            q_map[k] = "=".join(v)
        fragment = data.fragment

        self.tags.append(fragment)
        if "美国" in fragment:
            self.tags_arimician.append(fragment)
        result = {
            "type": "hysteria2",
            "tag": fragment,
            "server": server,
            "server_port": int(server_port),
            "password": password,
            "tls": {
                "enabled": True,
                "insecure": True,
                "server_name": q_map.get("sni")
            }

        }

        return result

    def parse_trojan(self, data):
        """

        """

        password, ip_port = data.netloc.split("@")
        server, server_port = ip_port.split(":")
        query = data.query.split("&")

        if server in self.un_used_list:
            return

        q_map = {}
        for q in query:
            k, *v = q.split("=")

            q_map[k] = "=".join(v)
        fragment = data.fragment

        self.tags.append(fragment)
        if "美国" in fragment:
            self.tags_arimician.append(fragment)
        result = {
            "type": "trojan",
            "tag": fragment,
            "server": server,
            "server_port": int(server_port),
            "password": password,
            "tls": {
                "enabled": True,
                "insecure": True,
                "server_name": q_map.get("sni")
            }

        }

        return result

    def get_download_url(self, user_name="JHC000abc", warehouse="ProxyParseForSing-box"):
        """

        """
        headers = {
            "referer": "https://www.jsdelivr.com/",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
        }

        url = f"https://api.github.com/repos/{user_name}/{warehouse}/commits/master"
        response = requests.get(url, headers=headers)

        contents_url = response.json()["files"][0]["contents_url"]
        response = requests.get(contents_url, headers=headers)
        return response.json()["download_url"]

    def process(self):
        """

        """
        response = self.get_book_data()
        response_data = response.text

        self.outbounds = []
        self.tags = []
        self.tags_arimician = []
        for node in self.decode_data(response_data.strip()):
            url_parse_result = parse.urlparse(parse.unquote(node))
            print(url_parse_result)
            self.parse_scheme(url_parse_result)

        main_json = self.get_main_json()
        with open(f"config_{datetime.now().strftime("%Y%m%d")}.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(main_json, indent=4, ensure_ascii=False))


if __name__ == '__main__':
    url = "https://raw.githubusercontent.com/snakem982/proxypool/main/source/v2ray-2.txt"
    pbu = ParseBookUrl(url)
    pbu.process()
    # print(pbu.get_download_url())
