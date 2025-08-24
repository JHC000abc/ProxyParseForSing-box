from parse_schem.base_parse import *


class ParseVless(BaseParse):

    def __init__(self):
        super().__init__()

    async def build_vless(self, parse_url):
        """

        :param parse_url:
        :return:
        """
        print(parse_url)
        netloc = parse_url.netloc
        uuid, server_port = netloc.split("@")
        server, port = server_port.split(":")
        query = {k: v[0] for k, v in parse.parse_qs(parse_url.query).items()}
        fragment = parse_url.fragment

        if query["path"] == "/":
            return

        res = {
            "type": "vless",
            "tag": fragment,
            "server": server,
            "server_port": int(port),
            "uuid": uuid,
            "transport": {
                "type": query['type'],
                "path": query['path'],
                "headers": {
                    "Host": query["host"]
                }
            }
        }

        if query.get('security') == "tls":
            res.update({
                "tls": {
                    "enabled": True,
                    "insecure": True,
                    "server_name": query["sni"]
                }
            })

        return res
