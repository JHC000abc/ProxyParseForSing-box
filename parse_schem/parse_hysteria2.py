from parse_schem.base_parse import *


class ParseHysteria2(BaseParse):

    def __init__(self):
        super().__init__()

    async def build_hysteria2(self, parse_url):
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
        insecure = True if query.get("insecure") == "1" else False
        out = {
            "type": "hysteria2",
            "tag": fragment,
            "server": server,
            "server_port": int(port),
            "password": password,
            "tls": {
                "enabled": True,
                "insecure": insecure,
            }
        }
        if query.get("sni"):
            out["tls"].update({"server_name": query["sni"]})

        if query.get("obfs"):
            out.update(
                {"obfs": {
                    "type": query["obfs"],
                }}
            )
            if query.get("obfs-password"):
                out["obfs"].update({
                    "password": query["obfs-password"],
                })
        return out
