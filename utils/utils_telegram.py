import os
from utils_cmd import AsyncCMD
import argparse
import asyncio
from datetime import datetime


class AsyncTelegram:
    """

    """

    def __init__(self):
        self.cmd = AsyncCMD()

    async def process(self, message, chat_id, token):
        """

        :param message:
        :param chat_id:
        :param token:
        :return:
        """
        cmd = f"curl -k --data chat_id='{chat_id}' --data 'text=[{datetime.now().strftime('%Y/%m/%d %H/%M/%S')}]({message})' 'https://api.telegram.org/bot{token}/sendMessage' "
        os.system(cmd)


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', "--messages", dest='messages', help='messages', required=True, nargs='+')
    parser.add_argument('-i', "--id", dest='id', help='id', default="")
    parser.add_argument('-t', "--token", dest='token', help='token',
                        default="")
    args = parser.parse_args()
    for message in args.messages:
        await AsyncTelegram().process(message, args.id, args.token)


if __name__ == '__main__':
    asyncio.run(main())
