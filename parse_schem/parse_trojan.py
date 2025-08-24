from parse_schem.base_parse import *


class ParseTrojan(BaseParse):

    def __init__(self):
        super().__init__()

    async def build_trojan(self, parse_url):
        """

        :param parse_url:
        :return:
        """
        print(parse_url)
        netloc = parse_url.netloc
        password, server_port = netloc.split("@")
        server, port = server_port.split(":")
        query = {k: v[0] for k, v in parse.parse_qs(parse_url.query).items()}
        fragment = parse_url.fragment

        res = {
            "type": "trojan",
            "tag": fragment,
            "server": server,
            "server_port": int(port),
            "password": password,
        }
        if query.get("allowInsecure") == "1":
            res.update({
                "tls": {
                    "enabled": True,
                    "insecure": True,
                    "server_name": query.get("peer", query.get("sni"))
                }
            })

        if query.get("wspath") and query.get("sni"):
            res.update({
                "transport": {
                    "type": query['ws'],
                    "path": query['wspath'],
                    "headers": {
                        "Host": query["sni"]
                    }
                }
            })

        return res
