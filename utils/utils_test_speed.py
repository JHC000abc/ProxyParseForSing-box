import re
import os
import json
from utils.utils_cmd import AsyncCMD
from utils.utils_encrypt import AsyncEncrypt
from settings import TEST_LISTEN_PORT, SING_BOX_PATH

try:
    from settings import SPEED_LIMIT
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
                    "url": "https://gemini.google.com/gem",
                    "interval": "0.1m"
                },
                node_conf
            ]

        }

    async def test_speed(self, node_conf, listen_port=None):
        """

        :param node_conf:
        :param listen_port:
        :return:
        """
        config = await self.get_test_conf(node_conf, listen_port)
        tmp_file_path = f"tmp_{await self.encrypt.make_md5(node_conf['tag'])}"
        try:
            with open(tmp_file_path, "w", encoding="utf-8") as f:
                f.write(json.dumps(config, indent=4, ensure_ascii=False))

            cmd = f"{SING_BOX_PATH} run -c {tmp_file_path}"
            async for msg, proc in self.cmd.run_cmd_async(cmd):
                # print(msg)
                match = re.search(r"available: (\d+)ms", msg)
                # lookup succeed for 丢弃 避免vmess 成功率低问题
                match_error = re.search(
                    r"context deadline exceeded|no recent network activity|unavailable: |unknown transport type|lookup succeed for",
                    msg)
                if match:
                    speed = match.group(1)
                    if speed:
                        speed = int(speed)
                        if SPEED_LIMIT:
                            if speed > SPEED_LIMIT:
                                return False, {}
                    res = {
                        f"{await self.encrypt.make_md5(str(node_conf))}": {
                            "node_info": node_conf,
                            "speed": speed,
                        }
                    }
                    proc.terminate()
                    return True, res
                elif match_error:
                    proc.terminate()
                    return False, {}
        except Exception:
            return False, {}
        finally:
            if os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)
