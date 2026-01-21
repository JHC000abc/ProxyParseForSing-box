import re
import os
import json
from utils.utils_cmd import AsyncCMD
from utils.utils_encrypt import AsyncEncrypt
from settings.setting import TEST_LISTEN_PORT, SING_BOX_PATH, TIMEOUT, TEST_IP_NODE, NODE_TEST_CONNECT_SPEED

try:
    from settings.setting import SPEED_LIMIT
except:
    SPEED_LIMIT = None


class TestSpeed:
    """

    """

    def __init__(self):
        self.encrypt = AsyncEncrypt()
        self.cmd = AsyncCMD()

    async def get_test_conf(self, node_conf, listen_port=None):
        """

        :param node_conf:
        :param listen_port:
        :return:
        """
        if not listen_port:
            listen_port = TEST_LISTEN_PORT

        return {
            "inbounds": [
                {
                    "type": "mixed",
                    "tag": "mixed-in",
                    "listen": "::",
                    "listen_port": listen_port,
                    "sniff": True
                }
            ],
            "outbounds": [
                {
                    "type": "urltest",
                    "tag": "AUTO-US",
                    "outbounds": [
                        node_conf["tag"]
                    ],
                    "url": f"{NODE_TEST_CONNECT_SPEED}",
                    "interval": "1m"
                },
                node_conf
            ]
        }

    async def close_cmd(self, proc):
        """

        :param proc:
        :return:
        """
        try:
            if proc:
                proc.terminate()
        except Exception as e:
            pass

    async def verify_forbidden_server(self, rules, data, server, tag=None):
        """

        :param rules:
        :param data:
        :param tag:
        :return:
        """
        data = data.strip()
        server = server.strip()

        for rule in rules:
            # 优化3: 利用 or 的短路机制。
            # 如果 data 匹配成功，re.match(rule, server) 将完全不会执行，节省计算资源。
            if re.match(rule, data) or re.match(rule, server):
                print(f"【成功匹配到禁止server规则】:{rule}<--->{data}{server}<--->{tag}")
                return True
        return False

    async def test_speed(self, node_conf, listen_port=None, forbidden_area_map={}, forbidden_area_re_map={}):
        """
        优化说明：
        1. 预编译所有正则表达式，避免循环内重复编译。
        2. 将 forbidden_area_map 的循环查找转换为单次正则匹配。
        """

        # --- 优化点1：预编译正则表达式 (提升循环内匹配速度) ---
        # 匹配速度
        PATTERN_SPEED = re.compile(r"available: (\d+)ms")
        # 匹配错误信息
        PATTERN_ERROR = re.compile(r"context deadline exceeded|no recent network activity|unknown transport type")
        # 匹配 curl 输出的 city 和 ip (保持原逻辑使用 match，即从行首匹配)
        PATTERN_AREA = re.compile(r'"city": "(.*?)",')
        PATTERN_IP = re.compile(r'"ip": "(.*)",')

        # --- 优化点2：构建“禁止区域”的联合正则 ---
        # 将 map 中的 key 和 硬编码的错误文本合并为一个正则： (Key1|Key2|...|400 Bad Request|Connection refused)
        # <span style="color: red;">假设 forbidden_area_map 的 key 都是字符串。使用了 re.escape 确保特殊字符不会破坏正则结构。</span>
        forbidden_keywords = list(forbidden_area_map.keys())
        forbidden_keywords.extend(["400 Bad Reques", "Connection refused"])  # 添加硬编码的错误条件

        if forbidden_keywords:
            # 只有当列表不为空时才编译，避免空正则报错
            # 这里的逻辑是：只要匹配到任意一个关键词，即为 True
            pattern_forbidden_check = re.compile('|'.join(map(re.escape, forbidden_keywords)))
        else:
            pattern_forbidden_check = None

        # --- 业务逻辑开始 ---
        config = await self.get_test_conf(node_conf, listen_port)
        tmp_file_path = f"tmp_{await self.encrypt.make_md5(node_conf['tag'])}"
        proc = None
        proc2 = None

        try:
            # <span style="color: red;">文件写入操作：IO密集型。如果 self.encrypt.make_md5 产生的文件名唯一且无冲突，此处逻辑安全。</span>
            with open(tmp_file_path, "w", encoding="utf-8") as f:
                f.write(json.dumps(config, indent=4, ensure_ascii=False))

            cmd = f"{SING_BOX_PATH} run -c {tmp_file_path}"
            cmd2 = f"curl {TEST_IP_NODE} -x 127.0.0.1:{listen_port} -m {TIMEOUT}"

            async for msg, proc in self.cmd.run_cmd_async(cmd):
                # 使用预编译对象进行搜索
                match_speed = PATTERN_SPEED.search(msg)

                # 如果匹配到了速度，就没有必要检查错误了，利用 if-elif 结构 (虽然原逻辑未互斥，但通常不会同时出现)
                if match_speed:
                    ip = node_conf["server"]
                    area = node_conf["tag"]
                    flag_area = False
                    flag_ip = False

                    # 启动第二个进程进行 curl 检测
                    async for msg2, proc2 in self.cmd.run_cmd_async(cmd2):
                        # 使用预编译对象匹配
                        match_area = PATTERN_AREA.match(msg2)
                        match_ip = PATTERN_IP.match(msg2)

                        if match_area:
                            area = match_area.group(1)
                            flag_area = True

                        if match_ip:
                            ip = match_ip.group(1)
                            flag_ip = True

                        # --- 优化点3：单次正则替代循环查找 ---
                        # 检查是否包含禁止关键词或错误信息
                        if pattern_forbidden_check and pattern_forbidden_check.search(msg2):
                            # <span style="color: red;">注意：原代码中打印 k 的逻辑在此被简化。如果需要具体知道是哪个词触发了禁止，需要 search().group()。这里为了性能只判断是否匹配。</span>
                            print(
                                f"【禁止区域/错误】 match:{pattern_forbidden_check.search(msg2).group()} server:{node_conf['server']} tag:{node_conf['tag']}")
                            await self.close_cmd(proc2)
                            return False, {}

                    await self.close_cmd(proc)

                    if not flag_ip or not flag_area:
                        return False, {}

                    node_conf["tag"] = f"{area}-{ip}-{await self.encrypt.make_md5(str(node_conf))}"

                    # 正则匹配剔除ip (调用之前的优化函数)
                    if forbidden_area_re_map:
                        if await self.verify_forbidden_server(forbidden_area_re_map, ip, node_conf['server'],
                                                              node_conf["tag"]):
                            return False, {}

                    # 类型转换移到确认需要使用之后
                    speed = int(match_speed.group(1))
                    print(node_conf["tag"], speed)

                    if SPEED_LIMIT and speed > SPEED_LIMIT:
                        print(f"[超时]:{node_conf['tag']},{node_conf}")
                        return False, {}

                    res = {
                        "node_info": node_conf,
                        "speed": speed,
                    }
                    return True, res

                # 只有没匹配到速度时，才检查错误，节省匹配次数
                elif PATTERN_ERROR.search(msg):
                    await self.close_cmd(proc)
                    return False, {}

        except Exception as e:
            # <span style="color: red;">添加了 traceback 打印，确保调试信息准确</span>
            import traceback
            print(f"Error in test_speed: {e}")
            traceback.print_exc()
            return False, {}

        finally:
            await self.close_cmd(proc)
            await self.close_cmd(proc2)

            if os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)
