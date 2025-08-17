# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@author: JHC000abc@gmail.com
@file: main.py
@time: 2025/8/17 15:37 
@desc: 

"""
from datetime import datetime
import json
from parse_node_snakem982 import ParseNodeSnakem982
from parse_node_sharkDoor import ParseNodesharkDoor

if __name__ == '__main__':
    p1 = ParseNodeSnakem982()
    p1.process()
    print(len(p1.outbounds))
    p2 = ParseNodesharkDoor()
    p2.process()
    print(len(p2.outbounds))

    stand_json = {
        "inbounds": p1.get_inbounds(),
        "outbounds": p1.get_outbounds() + p2.outbounds + p1.outbounds,
        "route": p1.get_route()
    }

    with open(f"config_{datetime.now().strftime("%Y%m%d")}.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(stand_json, indent=4, ensure_ascii=False))
