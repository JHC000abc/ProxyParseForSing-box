#!/usr/bin/python3
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
from settings.setting import SPEED_LIMIT
from parse_nodes.parse_node_snakem982 import ParseNodeSnakem982
from parse_nodes.parse_node_clashmeta import ParseNodeclashmeta
from parse_nodes.parse_node_sharkDoor import ParseNodesharkDoorV2
from parse_nodes.parse_node_sing_books import ParseNodeSingBooks
from parse_nodes.parse_node_clash import ParseNodeClash
from settings.setting import FORBIDDEN_AREA_FILE, FORBIDDEN_PROXY_FILE, MAX_CONCURRENCY, FORBIDDEN_SERVER_RE_FILE, \
    TIMEOUT, TEST_LISTEN_PORT
# os.environ["ALL_PROXY"] = "http://172.17.0.1:10808"


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


async def test_nodes_via_singbox_api(nodes_to_test, singbox_path="./plugins/sing-box"):
    """
    核心测速逻辑 + 详细日志
    """
    proxy_nodes = [n for n in nodes_to_test if n.get("type") not in ["direct", "block", "dns", "selector", "urltest"]]

    if not proxy_nodes:
        print("❌ 过滤后没有任何可测速的代理节点")
        return []

    print(f"📊 准备测速节点数量: {len(proxy_nodes)}")

    # ========== 强制修正数字类型 + Reality 补全 uTLS ==========
    def fix_types(node: dict) -> dict:
        # 数字字段强制转 int
        int_fields = ["server_port", "alter_id", "alterId", "port"]
        for field in int_fields:
            if field in node:
                try:
                    node[field] = int(node[field])
                except (ValueError, TypeError):
                    node[field] = 0

        if "alterId" in node:
            node["alter_id"] = int(node.pop("alterId") or 0)

        # Reality 必须开启 uTLS
        tls = node.get("tls")
        if isinstance(tls, dict):
            reality = tls.get("reality")
            if isinstance(reality, dict) and reality.get("enabled"):
                if "utls" not in tls or not isinstance(tls["utls"], dict):
                    tls["utls"] = {
                        "enabled": True,
                        "fingerprint": "chrome"
                    }
                else:
                    tls["utls"]["enabled"] = True
                    if not tls["utls"].get("fingerprint"):
                        tls["utls"]["fingerprint"] = "chrome"

        return node

    proxy_nodes = [fix_types(n.copy()) for n in proxy_nodes]
    # ========================================================

    test_config = {
        "log": {"level": "error"},
        "inbounds": [],
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
        json.dump(test_config, f, ensure_ascii=False, indent=2)

    print(f"📄 临时配置已写入: {test_config_path}")

    # 启动 sing-box
    print(f"⚙️ 启动 sing-box: {singbox_path}")
    process = subprocess.Popen(
        [singbox_path, "run", "-c", test_config_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # 等待并检查 API 是否就绪
    api_base = "http://127.0.0.1:9090"
    ready = False
    for i in range(15):
        await asyncio.sleep(1)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{api_base}/version", timeout=2) as resp:
                    if resp.status == 200:
                        version = await resp.json()
                        print(f"✅ Sing-box API 已就绪 (version: {version.get('version', 'unknown')})")
                        ready = True
                        break
        except Exception:
            print(f"⏳ 等待 API 就绪... ({i+1}/15)")

    if not ready:
        stdout, stderr = process.communicate(timeout=3)
        print("❌ Sing-box 未能正常启动，错误信息：")
        if stdout:
            print("STDOUT:\n", stdout)
        if stderr:
            print("STDERR:\n", stderr)
        process.terminate()
        if os.path.exists(test_config_path):
            os.remove(test_config_path)
        return []

    test_url = "https://www.gstatic.com/generate_204"
    print(f"🚀 开始并发测速，测试地址: {test_url}")
    print("-" * 80)

    # 并发测速
    async with aiohttp.ClientSession() as session:
        tasks = []
        for node in proxy_nodes:
            tag = node.get("tag", "")
            safe_tag = quote(tag, safe='')
            safe_url = quote(test_url, safe='')
            url = f"{api_base}/proxies/{safe_tag}/delay?timeout={SPEED_LIMIT}&url={safe_url}"
            tasks.append(test_single_node_api(session, url, node))

        results = await asyncio.gather(*tasks, return_exceptions=True)

    # 关闭进程
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()

    if os.path.exists(test_config_path):
        os.remove(test_config_path)

    # 统计结果
    valid_nodes = []
    fail_count = 0
    error_count = 0

    for result in results:
        if isinstance(result, Exception):
            error_count += 1
            print(f"💥 任务异常: {result}")
            continue

        if isinstance(result, tuple) and len(result) == 4:
            node_info, delay, status, msg = result
            if delay is not None:
                valid_nodes.append((node_info, delay))
                print(f"✅ {node_info['type']:<12} | {delay:>4} ms | {node_info['tag']}")
            else:
                fail_count += 1
                if fail_count <= 30:
                    print(f"❌ {node_info['type']:<12} | 失败 | status={status} | {msg} | {node_info['tag']}")
        else:
            error_count += 1
            print(f"💥 返回格式异常: {result}")

    print("-" * 80)
    print(f"📈 测速统计: 成功 {len(valid_nodes)} 个 | 失败 {fail_count} 个 | 异常 {error_count} 个")
    return valid_nodes


async def test_single_node_api(session, url, node_info):
    """
    返回: (node_info, delay, status_code, message)
    """
    try:
        timeout = aiohttp.ClientTimeout(total=SPEED_LIMIT / 1000 + 3)
        async with session.get(url, timeout=timeout) as response:
            status = response.status
            if status == 200:
                data = await response.json()
                delay = data.get("delay")
                if delay is not None and delay > 0:
                    return node_info, delay, status, "ok"
                else:
                    return node_info, None, status, f"无 delay 字段: {data}"
            else:
                text = await response.text()
                return node_info, None, status, text[:120]
    except asyncio.TimeoutError:
        return node_info, None, 0, "请求超时"
    except Exception as e:
        return node_info, None, 0, str(e)


async def main():
    lis1, lis2, lis3, lis4, lis5 = [], [], [], [], []

    # p1 = ParseNodeSnakem982()
    # lis1 = await p1.process()

    # p2 = ParseNodesharkDoorV2()
    # lis2 = await p2.process()

    # p3 = ParseNodeSingBooks()
    # lis3 = await p3.process()

    p4 = ParseNodeClash()
    lis4 = await p4.process()

    # p5 = ParseNodeclashmeta()
    # lis5 = await p5.process()

    all_nodes = lis1 + lis2 + lis3 + lis4 + lis5

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
    print("valid_results 数量:", len(valid_results) if valid_results else 0)

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