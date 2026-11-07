# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@author: JHC000abc@gmail.com
@file: parse_node_clash.py
@time: 2026/11/7 22:12 
@desc: 
https://sub.danhu.dpdns.org/paste/TG@FProxies261024fhU8Dbp/clash
"""
import asyncio
import re
import json
import yaml
import traceback
from parse_nodes.base import Base


class ParseNodeClash(Base):
    """
    解析 Clash 订阅配置并转换为 Sing-box 格式
    """

    def __init__(self):
        super().__init__()
        self.search_url = [
            "https://sub.danhu.dpdns.org/paste/TG@FProxies261024fhU8Dbp/clash"
        ]

    def convert_clash_to_singbox(self, clash_node):
        """
        核心逻辑：将 Clash 节点字典转换为 Sing-box Outbound 字典
        """
        n_type = clash_node.get("type")
        # 协议类型映射 (移除了 anytls，因为标准 sing-box 尚未支持)
        type_map = {
            "http": "http",
            "socks5": "socks",
            "ss": "shadowsocks",
            "vmess": "vmess",
            "vless": "vless",
            "trojan": "trojan",
            "hysteria2": "hysteria2"
        }

        sb_type = type_map.get(n_type)
        if not sb_type:
            # 如果不支持该协议（如 anytls），则直接跳过该节点
            return None

        name = clash_node.get("name", "Unknown")
        server = clash_node.get("server", "Unknown")
        port = clash_node.get("port", 0)

        sb_node = {
            # 生成唯一 Tag，防止重名导致 API 测速冲突
            "tag": f"{name}_{server}_{port}",
            "type": sb_type,
            "server": server,
            "server_port": int(port)
        }

        if clash_node.get("tfo"):
            sb_node["tcp_fast_open"] = True

        # 1. TLS 配置转换
        tls_enabled = clash_node.get("tls", False)
        # 【核心修复】：hysteria2 和 trojan 在 sing-box 中强制要求开启 TLS
        force_tls = sb_type in ["hysteria2", "trojan"]

        if tls_enabled or clash_node.get("reality-opts") or force_tls:
            tls_config = {"enabled": True}
            if clash_node.get("skip-cert-verify"):
                tls_config["insecure"] = True

            sni = clash_node.get("servername") or clash_node.get("sni")
            if sni:
                tls_config["server_name"] = sni

            if clash_node.get("client-fingerprint"):
                tls_config["utls"] = {
                    "enabled": True,
                    "fingerprint": clash_node.get("client-fingerprint")
                }

            if clash_node.get("reality-opts"):
                tls_config["reality"] = {
                    "enabled": True,
                    "public_key": clash_node["reality-opts"].get("public-key"),
                    "short_id": clash_node["reality-opts"].get("short-id")
                }
            sb_node["tls"] = tls_config

        # 2. 协议特定参数转换
        if sb_type in ["http", "socks"]:
            u = clash_node.get("username")
            p = clash_node.get("password")
            if u and str(u) not in ["None", "null", ""]: sb_node["username"] = str(u)
            if p and str(p) not in ["None", "null", ""]: sb_node["password"] = str(p)

        elif sb_type == "shadowsocks":
            sb_node["method"] = clash_node.get("cipher")
            sb_node["password"] = clash_node.get("password")

        elif sb_type == "vmess":
            sb_node["uuid"] = clash_node.get("uuid")
            sb_node["security"] = clash_node.get("cipher", "auto")
            sb_node["alter_id"] = clash_node.get("alterId", 0)

        elif sb_type == "vless":
            sb_node["uuid"] = clash_node.get("uuid")
            if clash_node.get("flow"):
                sb_node["flow"] = clash_node.get("flow")

        elif sb_type in ["trojan", "hysteria2"]:
            sb_node["password"] = clash_node.get("password")

        # 3. 传输层 (Transport) 转换
        network = clash_node.get("network")
        if network == "ws":
            ws_opts = clash_node.get("ws-opts", {})
            transport = {
                "type": "ws",
                "path": ws_opts.get("path", "/")
            }
            if ws_opts.get("headers"):
                transport["headers"] = ws_opts["headers"]
            sb_node["transport"] = transport
        elif network == "grpc":
            grpc_opts = clash_node.get("grpc-opts", {})
            transport = {
                "type": "grpc",
                "service_name": grpc_opts.get("grpc-service-name", "")
            }
            sb_node["transport"] = transport

        return sb_node

    async def parse_search(self, html):
        """
        解析 YAML 并调用转换函数
        """
        outbounds = []
        try:
            data = yaml.safe_load(html)
            if not data or "proxies" not in data:
                print("未找到有效的 proxies 字段")
                return outbounds

            proxies = data["proxies"]
            for p in proxies:
                sb_node = self.convert_clash_to_singbox(p)
                if sb_node:
                    outbounds.append(sb_node)
            return outbounds
        except yaml.YAMLError as e:
            print(f"YAML 解析失败: {e}")
            return outbounds
        except Exception as e:
            print(f"解析过程发生错误: {e}")
            return outbounds

    async def parse_detail(self, html):
        # Clash 订阅通常不需要 parse_detail，保留空实现兼容 Base 类
        pass

    async def process(self):
        """
        获取并解析节点，将有效节点存入 self.success_list 并返回
        """
        try:
            for url in self.search_url:
                # print("url:", url)
                try:
                    search_html = await self.net.fetch_url_get(url=url, headers=self.headers, proxy=False)
                except Exception as e:
                    print(f"请求失败: {e}")
                    continue

                search_result = await self.parse_search(search_html)
                print(f"成功解析并转换了 {len(search_result)} 个节点")

                for node in search_result:
                    # 【核心修复】：将解析出的节点追加到 Base 类定义的 success_list 中
                    self.success_list.append(node)

        except Exception as e:
            print(f"ParseNodeClash process error: {traceback.format_exc()}")

        return self.success_list
