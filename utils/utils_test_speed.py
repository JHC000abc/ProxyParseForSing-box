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

    async def verify_forbidden_server(self, rules, data):
        """

        :param rules:
        :param data:
        :return:
        """
        for rule, _ in rules.items():
            match = re.match(rule, data)
            if match:
                print(f"成功匹配到规则:{rule}<--->{data}")
                return True
        return False

    async def test_speed(self, node_conf, listen_port=None, forbidden_area_map={}, forbidden_area_re_map={}):
        """

        :param node_conf:
        :param listen_port:
        :param forbidden_area_map:
        :param forbidden_area_re_map:
        :return:
        """
        config = await self.get_test_conf(node_conf, listen_port)
        tmp_file_path = f"tmp_{await self.encrypt.make_md5(node_conf['tag'])}"
        proc = None
        proc2 = None
        try:
            with open(tmp_file_path, "w", encoding="utf-8") as f:
                f.write(json.dumps(config, indent=4, ensure_ascii=False))

            cmd = f"{SING_BOX_PATH} run -c {tmp_file_path}"
            cmd2 = f"curl {TEST_IP_NODE} -x 127.0.0.1:{listen_port} -m {TIMEOUT}"
            async for msg, proc in self.cmd.run_cmd_async(cmd):
                match_speed = re.search(r"available: (\d+)ms", msg)
                # lookup succeed for 丢弃 避免vmess 成功率低问题
                match_error = re.search(
                    r"context deadline exceeded|no recent network activity|unavailable: |unknown transport type|lookup succeed for",
                    msg)
                if match_speed:
                    ip = node_conf["server"]
                    area = node_conf["tag"]
                    flag_area = False
                    flag_ip = False
                    async for msg2, proc2 in self.cmd.run_cmd_async(cmd2):
                        match_area = re.match("地址	: (.*)", msg2)
                        match_ip = re.match("IP	: (.*)", msg2)
                        if match_area:
                            area = match_area.group(1)
                            flag_area = True

                        if match_ip:
                            ip = match_ip.group(1)
                            flag_ip = True

                        for k, v in forbidden_area_map.items():
                            if k in msg2 or "400 Bad Reques" in msg2 or "Connection refused" in msg2:
                                print(f"forbidden area {k} {node_conf['server']}")
                                await self.close_cmd(proc2)
                                return False, {}

                    await self.close_cmd(proc)

                    if not flag_ip or not flag_area:
                        return False, {}

                    node_conf["tag"] = f"{area}-{ip}-{await self.encrypt.make_md5(str(node_conf))}"

                    # 正则匹配剔除ip
                    if forbidden_area_re_map:
                        if await self.verify_forbidden_server(forbidden_area_re_map, ip):
                            return False, {}

                    speed = match_speed.group(1)
                    speed = int(speed)
                    print(area, ip, f"{speed} ms")
                    if SPEED_LIMIT:
                        if speed > SPEED_LIMIT:
                            return False, {}
                    res = {
                        "node_info": node_conf,
                        "speed": speed,
                    }
                    return True, res
                elif match_error:
                    await self.close_cmd(proc)
                    return False, {}
        except Exception as e:
            return False, {}
        finally:
            await self.close_cmd(proc)
            await self.close_cmd(proc2)

            if os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)
