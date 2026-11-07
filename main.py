# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@author: JHC000abc@gmail.com
@file: main.py
@time: 2025/8/17 15:37 
@desc: 
"""
import os
import asyncio
import traceback
import subprocess
import json
import aiohttp
from urllib.parse import quote

from parse_nodes.parse_node_snakem982 import ParseNodeSnakem982
# from parse_nodes.parse_node_sharkDoor import ParseNodesharkDoorV2
from parse_nodes.parse_node_sing_books import ParseNodeSingBooks
from parse_nodes.parse_node_clash import ParseNodeClash
from settings.setting import FORBIDDEN_AREA_FILE, FORBIDDEN_PROXY_FILE, MAX_CONCURRENCY, FORBIDDEN_SERVER_RE_FILE, \
    TIMEOUT, TEST_LISTEN_PORT


async def filter(file):
    tag_map = {}
    if not os.path.exists(file):
        return tag_map
    try:
        with open(file, "r", encoding="utf-8") as f:
            for line in f:
                new_line = line.strip()
                if new_line and not new_line.startswith("#"):
                    tag_map[new_line] = 1
    except FileNotFoundError:
        print(f"Warning: '{file}' not found.")
    return tag_map


async def test_nodes_via_singbox_api(nodes_to_test, singbox_path="./sing-box"):
    """
    核心测速逻辑：利用 Sing-box 的 Clash API 进行高精度并发测速
    """
    # 过滤掉不需要测速的内置节点
    proxy_nodes = [n for n in nodes_to_test if n.get("type") not in ["direct", "block", "dns", "selector", "urltest"]]

    if not proxy_nodes:
        return []

    # 1. 生成专门用于测速的临时配置
    test_config = {
        "log": {"level": "error"},  # 关闭日志干扰
        "inbounds": [],  # 不需要入站，只测出站
        "outbounds": proxy_nodes,
        "experimental": {
            "clash_api": {
                "external_controller": "127.0.0.1:9090",
                "secret": ""
            }
        }
    }

    test_config_path = "test_speed_config.json"
    with open(test_config_path, "w", encoding="utf-8") as f:
        json.dump(test_config, f, ensure_ascii=False)

    print("⚙️ 启动 sing-box 核心进行 API 测速...")
    process = subprocess.Popen(
        [singbox_path, "run", "-c", test_config_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    # 等待 API 端口就绪
    await asyncio.sleep(2)

    api_base = "http://127.0.0.1:9090"
    test_url = "https://www.gstatic.com/generate_204"

    # 2. 并发请求 API 获取真实延迟
    async with aiohttp.ClientSession() as session:
        tasks = []
        for node in proxy_nodes:
            tag = node["tag"]
            # Tag 中包含 Emoji 和特殊字符，必须进行 URL Encode
            safe_tag = quote(tag, safe='')
            safe_url = quote(test_url, safe='')
            url = f"{api_base}/proxies/{safe_tag}/delay?timeout=5000&url={safe_url}"
            tasks.append(test_single_node_api(session, url, node))

        results = await asyncio.gather(*tasks, return_exceptions=True)

    # 3. 测速完成，关闭 sing-box 进程并清理临时文件
    process.terminate()
    process.wait()
    if os.path.exists(test_config_path):
        os.remove(test_config_path)

    # 4. 整理有效结果
    valid_nodes = []
    for result in results:
        if isinstance(result, tuple):
            node_info, delay = result
            if delay is not None:
                valid_nodes.append((node_info, delay))
                print(f"✅ 协议: {node_info['type']:<10} | 延迟: {delay:<4} ms | 节点: {node_info['tag']}")

    return valid_nodes


async def test_single_node_api(session, url, node_info):
    try:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                if "delay" in data:
                    return node_info, data["delay"]
            return node_info, None
    except Exception:
        return node_info, None


async def main():
    lis1, lis2, lis3, lis4 = [], [], [], []

    p1 = ParseNodeSnakem982()
    lis1 = await p1.process()

    # p2 = ParseNodesharkDoorV2()
    # lis2 = await p2.process()

    p3 = ParseNodeSingBooks()
    lis3 = await p3.process()

    p4 = ParseNodeClash()
    lis4 = await p4.process()

    all_nodes = lis1 + lis2 + lis3 + lis4

    un_used_tag_map = await filter(FORBIDDEN_PROXY_FILE)

    # 1. 基础过滤
    nodes_to_test = []
    for info in all_nodes:
        tag = info.get("tag")
        if tag and not un_used_tag_map.get(tag):
            nodes_to_test.append(info)

    if not nodes_to_test:
        print("No valid nodes to test after filtering.")
        return

    # 2. 节点去重 (基于 server:port)
    unique_nodes = []
    repeat_recode_map = {}
    for info in nodes_to_test:
        repeat_check_tag = f"{info.get('server')}_{info.get('server_port')}"
        if repeat_recode_map.get(repeat_check_tag) is None:
            unique_nodes.append(info)
            repeat_recode_map[repeat_check_tag] = 1

    print(f"🔍 去重后剩余待测试节点数量: {len(unique_nodes)}")
    print(f"🚀 开始通过 Sing-box API 进行并发测速...")

    # 3. 调用 API 测速
    valid_results = await test_nodes_via_singbox_api(unique_nodes, singbox_path="./plugins/sing-box")

    if not valid_results:
        print("❌ 未获取到任何有效节点。")
        return

    # 4. 按延迟排序并保存
    valid_results.sort(key=lambda x: x[1])

    speed_map = {}
    outbounds = []
    tags = []

    for node_info, delay in valid_results:
        tag = node_info["tag"]
        scheme = node_info["type"]
        speed_map[tag] = [delay, scheme, node_info]
        outbounds.append(node_info)
        tags.append(tag)

    # Save the results
    await p4.save_result_json(tags, outbounds, tags)
    print(f"🎉 测速完成，成功保存 {len(outbounds)} 个可用节点！")


if __name__ == '__main__':
    asyncio.run(main())