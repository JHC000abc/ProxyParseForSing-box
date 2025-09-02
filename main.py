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
from parse_nodes.parse_node_snakem982 import ParseNodeSnakem982
from parse_nodes.parse_node_sharkDoor import ParseNodesharkDoor
from utils.utils_test_speed import TestSpeed
from settings.setting import FORBIDDEN_AREA_FILE, FORBIDDEN_PROXY_FILE, MAX_CONCURRENCY, FORBIDDEN_SERVER_RE_FILE, \
    TIMEOUT, TEST_LISTEN_PORT


async def filter(file):
    """
    Loads a list of unused proxy tags from a file into a dictionary.

    :param file: Path to the file containing unused proxy tags.
    :return: A dictionary mapping unused tags to a value (1).
    """
    tag_map = {}
    if not os.path.exists(FORBIDDEN_PROXY_FILE):
        return tag_map
    try:
        with open(file, "r", encoding="utf-8") as f:
            for line in f:
                tag_map[line.strip()] = 1
    except FileNotFoundError:
        print(f"Warning: '{file}' not found. Skipping unused proxy filtering.")
    return tag_map


async def main():
    """
    Fetches proxy nodes from multiple sources, filters out unused ones,
    tests their speed with a limited concurrency, and saves the results.
    """
    p1 = ParseNodeSnakem982()
    lis1 = await p1.process()

    p2 = ParseNodesharkDoor()
    lis2 = await p2.process()
    # lis2 = []

    test_speed_instance = TestSpeed()

    # Combine nodes from different subscriptions
    all_nodes = lis1 + lis2

    # Get the list of unused nodes from the file
    un_used_tag_map = await filter(FORBIDDEN_PROXY_FILE)
    forbidden_area_map = await filter(FORBIDDEN_AREA_FILE)
    forbidden_area_re_map = await filter(FORBIDDEN_SERVER_RE_FILE)

    nodes_to_test = []
    for info in all_nodes:
        tag = info["tag"]
        if not un_used_tag_map.get(tag):
            nodes_to_test.append(info)

    if not nodes_to_test:
        print("No valid nodes to test after filtering.")
        return

    print(f"准备测试 {len(nodes_to_test)} 个代理节点...")

    # Set up a semaphore to limit concurrency
    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)

    async def test_node_with_semaphore(info, port, forbidden_area_map, forbidden_area_re_map):
        async with semaphore:
            try:
                return await asyncio.wait_for(
                    test_speed_instance.test_speed(info, port, forbidden_area_map, forbidden_area_re_map),
                    timeout=TIMEOUT
                )
            except asyncio.TimeoutError:
                print(f"[超时] 节点 '{info.get('tag', 'N/A')}' 在 {TIMEOUT} 秒内未完成测试。")
                return None  # 或者返回一个特定的错误标记
            except Exception as e:
                print(f"[错误] 测试节点 '{info.get('tag', 'N/A')}' 时发生异常: {e}")
                print(traceback.print_exc())
                return None

            # return await test_speed_instance.test_speed(info, port, forbidden_area_map, forbidden_area_re_map)

    tasks = []
    start_listen_port = TEST_LISTEN_PORT
    repeat_recode_map = {}
    for info in nodes_to_test:
        repeat_check_tag = f"{info['server']}_{info['port']}"
        if repeat_recode_map.get(repeat_check_tag) is None:
            tasks.append(test_node_with_semaphore(info, start_listen_port, forbidden_area_map, forbidden_area_re_map))
            start_listen_port += 1
            repeat_recode_map[repeat_check_tag] = 1

    print(f"去重后剩余待测试节点数量 {len(repeat_recode_map)}...")
    print(f"开始并发测试，最大并发量为 {MAX_CONCURRENCY}...")

    results = await asyncio.gather(*tasks, return_exceptions=True)

    speed_map = {}
    outbounds = []
    tags = []
    repeat_server_record = {}

    for i, result in enumerate(results):
        if not result:
            continue
        test_speed_status, info_speed = result

        if test_speed_status is False:
            continue

        node_info = info_speed["node_info"]
        tag = node_info["tag"]
        server = node_info["server"]
        speed = info_speed["speed"]

        if repeat_server_record.get(server) is None:
            scheme = node_info["type"]
            speed_map[tag] = [speed, scheme, node_info]
            outbounds.append(node_info)
            tags.append(tag)
            repeat_server_record[server] = 1
            print(f"协议: {scheme}\t节点: {tag}\t速度: {speed} ms")

    if not outbounds:
        print("未获取到任何有效节点。")
        return

    # Save the results
    await p1.save_result_json(tags, outbounds, tags)


if __name__ == '__main__':
    asyncio.run(main())
