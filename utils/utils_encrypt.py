import hashlib
from base64 import b64decode


class AsyncEncrypt:
    """

    """

    async def base64_decode(self, data):
        """

        :param data:
        :return:
        """
        return b64decode(data).decode("utf-8").strip()

    async def make_md5(self, data):
        """

        :param data:
        :return:
        """
        md5_hash = hashlib.md5()
        md5_hash.update(data.encode('utf-8'))
        hex_digest = md5_hash.hexdigest()
        return hex_digest
