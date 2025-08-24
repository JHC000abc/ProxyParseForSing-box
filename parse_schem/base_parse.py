from base64 import b64decode
from urllib import parse


class BaseParse:
    """

    """

    def parse_base64(self, data):
        """

        :param data:
        :return:
        """
        return b64decode(data).decode("utf-8").strip()
