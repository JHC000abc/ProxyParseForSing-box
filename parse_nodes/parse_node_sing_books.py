# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@author: JHC000abc@gmail.com
@file: parse_node_sing_books.py
@time: 2025/12/11 15:37 
@desc: 
"""
import asyncio
import json
import traceback
from parse_nodes.base import Base


class ParseNodeSingBooks(Base):
    """
    解析 Sing-box JSON 订阅配置
    """

    def __init__(self):
        super().__init__()
        self.search_url = [
            "https://gitlab.com/free9999/ipupdate/-/raw/master/backup/img/1/2/ipp/singbox/2/config.json",
            "https://www.67867867.xyz/Alvin9999/PAC/refs/heads/master/backup/img/1/2/ip/singbox/2/config.json",
            "https://www.67867867.xyz/Alvin9999/PAC/refs/heads/master/backup/img/1/2/ipp/singbox/1/config.json"
        ]

    async def parse_search(self, html):
        """
        解析 JSON 并提取有效的 outbound 节点
        """
        valid_outbounds = []
        try:
            data = json.loads(html)
            outbounds = data.get("outbounds", [])

            # 必须过滤掉非实体代理节点，否则 main.py 测速时会因为缺少 server 字段而报错
            invalid_types = ["direct", "block", "dns", "selector", "urltest"]

            for out in outbounds:
                if out.get("type") in invalid_types:
                    continue
                # 确保是有效的代理节点（包含 server 和 server_port）
                if "server" in out and "server_port" in out:
                    valid_outbounds.append(out)

            return valid_outbounds
        except json.JSONDecodeError:
            print("❌ JSON 解析失败，可能返回的不是标准 JSON 格式。")
            return []
        except Exception as e:
            print(f"❌ 解析 outbound 发生未知错误: {e}")
            return []

    async def parse_detail(self, html):
        # 此类为 JSON 解析，不需要 HTML 解析方法，留空兼容 Base 类
        pass

    async def process(self):
        """
        获取并解析节点，将有效节点存入 self.success_list 并返回
        """
        for url in self.search_url:
            print(f"🔗 Fetching sing-box config from: {url}")
            try:
                # 注意：如果当前环境没有运行全局代理，请求 gitlab 可能会超时。
                # 如果一直卡住或报错，请将 proxy=True 改为 proxy=False
                search_html = await self.net.fetch_url_get(url=url, headers=self.headers, proxy=True)
            except Exception as e:
                print(f"⚠️ 请求失败 {url}: {e}")
                continue  # 【修复】：继续请求下一个 URL，而不是直接 return

            search_result = await self.parse_search(search_html)
            print(f"✅ 成功从该链接解析了 {len(search_result)} 个实体节点")

            for i in search_result:
                try:
                    # 生成唯一 Tag，防止重名
                    base_tag = i.get("tag", "Unknown")
                    server = i.get("server", "Unknown")
                    port = i.get("server_port", 0)
                    tag = f"{base_tag}_{server}_{port}"

                    i["tag"] = tag

                    # 【核心修复】：将节点追加到 Base 类定义的 success_list 中
                    self.success_list.append(i)
                except Exception as e:
                    print(f"⚠️ 处理单个节点时出错: {e}")
                    continue

        # 基于 Tag 进行去重
        unique_nodes = {}
        for node in self.success_list:
            tag = node.get("tag")
            if tag and tag not in unique_nodes:
                unique_nodes[tag] = node

        self.success_list = list(unique_nodes.values())
        print(f"🎉 SingBooks 最终获取到 {len(self.success_list)} 个有效且不重复的节点。")

        return self.success_list
