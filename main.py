# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@author: JHC000abc@gmail.com
@file: main.py
@time: 2025/8/17 15:37 
@desc: 

"""
import asyncio
from parse_nodes.parse_node_snakem982 import ParseNodeSnakem982
from parse_nodes.parse_node_sharkDoor import ParseNodesharkDoor
from test_speed import TestSpeed



async def filter(file="./un_used_proxy.list"):
    """

    :param file:
    :return:
    """
    un_used_tag_map = {}
    with open(file, "r", encoding="utf-8") as f:
        for i in f:
            un_used_tag_map[i.strip()] = 1
    return un_used_tag_map


async def main():
    p1 = ParseNodeSnakem982()
    lis1 = await p1.process()
    p2 = ParseNodesharkDoor()
    lis2 = await p2.process()
    test_speed_instance = TestSpeed()

    # Combine the lists of nodes
    all_nodes = lis1 + lis2

    un_used_tag_map = await filter()

    # Create a list of coroutines (tasks) to be run concurrently.
    # We only create tasks for nodes that are not in the 'un_used' list.
    tasks = []
    nodes_to_test = []
    start_listen_port = 10900
    for info in all_nodes:
        tag = info["tag"]
        if not un_used_tag_map.get(tag):
            tasks.append(test_speed_instance.test_speed(info, start_listen_port))
            nodes_to_test.append(info)
            start_listen_port += 1

    print(f"开始并发测试 {len(tasks)} 个代理节点...")

    results = await asyncio.gather(*tasks, return_exceptions=True)

    speed_map = {}
    outbounds = []
    tags = []

    # Process the results
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            # Handle potential exceptions from the tasks (e.g., timeouts)
            print(f"节点测试失败: {nodes_to_test[i]['tag']} - {result}")
            continue
        if result:
            status, speed = result
            info = nodes_to_test[i]
            tag = info["tag"]
            scheme = info["type"]

            if status:
                speed_map[tag] = [speed, scheme, info]
                outbounds.append(info)
                tags.append(tag)

    for tag, (speed_res, scheme, info) in speed_map.items():
        speed = [v["speed"] for k,v in speed_res.items()][0]
        print(f"协议: {scheme}\t节点: {tag}\t速度: {speed} ms")

    await p1.save_result_json(tags, outbounds, tags)




if __name__ == '__main__':
    asyncio.run(main())
