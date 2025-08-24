import json
from parse_schem.base_parse import *


class ParseVmess(BaseParse):

    def __init__(self):
        super().__init__()

    async def build_vmess(self, parse_url):
        """

        :param parse_url:
        :return:
        """
        print(parse_url)
        if not parse_url.path:
            netloc = self.parse_base64(parse_url.netloc if parse_url.netloc.endswith("=") else parse_url.netloc + "=")
        else:
            netloc = self.parse_base64(parse_url.netloc + parse_url.path if parse_url.netloc.endswith(
                "=") else parse_url.netloc + parse_url.path + "=")
        if not netloc.endswith('}'):
            netloc += '"}'

        netloc = json.loads(netloc)
        if not netloc.get('host'):
            return

        res = {
            "type": "vmess",
            "tag": netloc['ps'],
            "server": netloc['add'],
            "server_port": int(netloc['port']),
            "uuid": netloc['id'],
            "tls": {
                "enabled": True if netloc['tls'] else False,
            },
            "transport": {
                "type": netloc['net'],
                "path": netloc['path'],
                "headers": {
                    "Host": netloc['host']
                }
            }
        }
        if netloc.get('scy'):
            res.update({"security": netloc['scy']})

        return res
