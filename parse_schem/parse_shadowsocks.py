import json
from parse_schem.base_parse import *


class ParseShadowSocks(BaseParse):

    def __init__(self):
        super().__init__()

    async def build_shadowsocks(self, parse_url):
        """

        :param parse_url:
        :return:
        """
        print(parse_url)
        netloc = parse_url.netloc
        fragment = parse_url.fragment
        path = parse_url.path
        line = netloc + path
        if line.endswith("="):
            data = self.parse_base64(line if line.endswith("=") else line + "=")
            if len(data.split("@")) == 2:
                m_p, s_p = data.split("@")
                method, password = m_p.split(":")
                server, port = s_p.split(":")
            else:
                *other, server_port = data.split("@")
                other = "@".join(other)
                server, port = server_port.split(":")
                method, *password = other.split(":")
                password = ":".join(password)
        else:
            m_p, *s_p = line.split("@")
            if len(line.split("@")) == 2:
                try:
                    data = self.parse_base64(m_p if m_p.endswith("=") else m_p + "=")
                    method, password = data.split(":")
                    server, port = "@".join(s_p).split(":")
                except Exception as e:
                    raise

            elif len(line.split("@")) < 2:
                data = self.parse_base64(line if line.endswith("=") else line + "=")
                m_p, *s_p = data.split("@")
                method, password = m_p.split(":")
                server, port = "@".join(s_p).split(":")

            else:
                *other, server_port = line.split("@")
                other = "@".join(other)
                data = self.parse_base64(other if other.endswith("=") else other + "=")
                server, port = server_port.split(":")
                method, password = data.split(":")
        port = port.strip("/")

        res = {
            "type": "shadowsocks",
            "tag": fragment,
            "server": server,
            "server_port": int(port),
            "method": method,
            "password": password
        }

        return res
