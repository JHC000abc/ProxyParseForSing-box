# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@author: JHC000abc@gmail.com
@file: parse_node_clashmeta.py
@time: 2026/11/9 21:41 
@desc: 

"""
#!/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@author: JHC000abc@gmail.com
@file: parse_node_share_links.py
@time: 2025/12/11
@desc: 从 URL 下载纯文本分享链接并解析
"""

import base64
import json
import re
import urllib.parse
from typing import Any, Dict, List, Optional

from parse_nodes.base import Base


class ParseNodeclashmeta(Base):
    """
    从 URL 下载一行一个分享链接的纯文本，解析成节点
    """

    def __init__(self):
        super().__init__()
        # 把你要订阅的纯文本链接放这里
        self.search_url = [
            # 示例，换成你自己的
            "https://raw.githubusercontent.com/Barabama/FreeNodes/refs/heads/main/nodes/clashmeta.txt",
            "https://raw.githubusercontent.com/Barabama/FreeNodes/refs/heads/main/nodes/clashmeta.txt",
        ]

    @staticmethod
    def _safe_b64decode(s: str) -> bytes:
        s = s.strip().replace('-', '+').replace('_', '/')
        pad = 4 - len(s) % 4
        if pad != 4:
            s += '=' * pad
        try:
            return base64.b64decode(s)
        except Exception:
            return b''

    def _parse_line(self, line: str) -> Optional[Dict[str, Any]]:
        line = line.strip()
        if not line or line.startswith('#') or '未找到有效' in line or '成功解析' in line:
            return None

        try:
            # ---------- ss ----------
            if line.startswith('ss://'):
                rest = line[5:]
                name = ''
                if '#' in rest:
                    rest, name = rest.rsplit('#', 1)
                    name = urllib.parse.unquote(name)

                if '@' not in rest:
                    decoded = self._safe_b64decode(rest.split('?')[0]).decode('utf-8', errors='ignore')
                    if '@' not in decoded:
                        return None
                    method_pass, server_port = decoded.rsplit('@', 1)
                else:
                    method_pass, server_port = rest.split('?')[0].rsplit('@', 1)

                method, password = method_pass.split(':', 1)
                host, port = server_port.rsplit(':', 1)
                return {
                    "type": "shadowsocks",
                    "tag": name or f"ss-{host}-{port}",
                    "server": host,
                    "server_port": int(port),
                    "method": method,
                    "password": password,
                }

            # ---------- vmess ----------
            if line.startswith('vmess://'):
                data = self._safe_b64decode(line[8:].split('#')[0]).decode('utf-8', errors='ignore')
                conf = json.loads(data)
                return {
                    "type": "vmess",
                    "tag": conf.get('ps') or f"vmess-{conf.get('add')}-{conf.get('port')}",
                    "server": conf.get('add'),
                    "server_port": int(conf.get('port', 0)),
                    "uuid": conf.get('id'),
                    "alter_id": int(conf.get('aid', 0)),
                    "security": conf.get('scy', 'auto'),
                }

            # ---------- vless ----------
            if line.startswith('vless://'):
                name = ''
                if '#' in line:
                    line, name = line.rsplit('#', 1)
                    name = urllib.parse.unquote(name)

                parsed = urllib.parse.urlparse(line)
                qs = {k: v[0] for k, v in urllib.parse.parse_qs(parsed.query).items()}

                node = {
                    "type": "vless",
                    "tag": name or f"vless-{parsed.hostname}-{parsed.port}",
                    "server": parsed.hostname,
                    "server_port": parsed.port or 443,
                    "uuid": parsed.username,
                    "flow": qs.get('flow', ''),
                }

                security = qs.get('security', '')
                if security in ('tls', 'reality'):
                    tls = {
                        "enabled": True,
                        "server_name": qs.get('sni', parsed.hostname),
                        "insecure": qs.get('insecure', '0') in ('1', 'true'),
                    }
                    if security == 'reality':
                        tls["reality"] = {
                            "enabled": True,
                            "public_key": qs.get('pbk', ''),
                            "short_id": qs.get('sid', ''),
                        }
                    node["tls"] = tls

                net = qs.get('type', 'tcp')
                if net == 'ws':
                    node["transport"] = {
                        "type": "ws",
                        "path": qs.get('path', '/'),
                        "headers": {"Host": qs.get('host', parsed.hostname)}
                    }
                elif net == 'grpc':
                    node["transport"] = {
                        "type": "grpc",
                        "service_name": qs.get('serviceName', '')
                    }

                return node

            # ---------- trojan ----------
            if line.startswith('trojan://'):
                name = ''
                if '#' in line:
                    line, name = line.rsplit('#', 1)
                    name = urllib.parse.unquote(name)

                parsed = urllib.parse.urlparse(line)
                qs = {k: v[0] for k, v in urllib.parse.parse_qs(parsed.query).items()}

                return {
                    "type": "trojan",
                    "tag": name or f"trojan-{parsed.hostname}-{parsed.port}",
                    "server": parsed.hostname,
                    "server_port": parsed.port or 443,
                    "password": parsed.username,
                    "tls": {
                        "enabled": True,
                        "server_name": qs.get('sni', parsed.hostname),
                        "insecure": qs.get('insecure', '0') in ('1', 'true'),
                    }
                }

            # ---------- hysteria2 ----------
            if line.startswith(('hysteria2://', 'hy2://')):
                name = ''
                if '#' in line:
                    line, name = line.rsplit('#', 1)
                    name = urllib.parse.unquote(name)

                parsed = urllib.parse.urlparse(line)
                qs = {k: v[0] for k, v in urllib.parse.parse_qs(parsed.query).items()}

                return {
                    "type": "hysteria2",
                    "tag": name or f"hy2-{parsed.hostname}-{parsed.port}",
                    "server": parsed.hostname,
                    "server_port": parsed.port or 443,
                    "password": parsed.username,
                    "tls": {
                        "enabled": True,
                        "server_name": qs.get('sni', parsed.hostname),
                        "insecure": True,
                    }
                }

        except Exception:
            return None

        return None

    async def parse_search(self, html: str) -> List[Dict[str, Any]]:
        valid = []
        for line in html.splitlines():
            node = self._parse_line(line)
            if node and "server" in node and "server_port" in node:
                valid.append(node)
        return valid

    async def parse_detail(self, html):
        pass

    async def process(self):
        for url in self.search_url:
            print(f"🔗 Fetching share links from: {url}")
            try:
                # 需要代理就保持 proxy=True，不需要就改成 False
                search_html = await self.net.fetch_url_get(url=url, headers=self.headers, proxy=True)
            except Exception as e:
                print(f"⚠️ 请求失败 {url}: {e}")
                continue

            search_result = await self.parse_search(search_html)
            print(f"✅ 成功从该链接解析了 {len(search_result)} 个节点")

            for i in search_result:
                try:
                    base_tag = i.get("tag", "Unknown")
                    server = i.get("server", "Unknown")
                    port = i.get("server_port", 0)
                    # 清理 tag 特殊字符
                    clean_tag = re.sub(r'[^\w\-\.\u4e00-\u9fff]', '_', str(base_tag))
                    i["tag"] = f"{clean_tag}_{server}_{port}"
                    self.success_list.append(i)
                except Exception as e:
                    print(f"⚠️ 处理单个节点时出错: {e}")
                    continue

        # 去重
        unique_nodes = {}
        for node in self.success_list:
            tag = node.get("tag")
            if tag and tag not in unique_nodes:
                unique_nodes[tag] = node

        self.success_list = list(unique_nodes.values())
        print(f"🎉 ShareLinks 最终获取到 {len(self.success_list)} 个有效且不重复的节点。")
        return self.success_list