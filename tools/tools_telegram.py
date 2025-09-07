import os
from utils.utils_cmd import AsyncCMD
import argparse
import asyncio
from utils.utils_times import UtilsTimes


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
        message = f"```\n{message}\n```"
        text = f"[{UtilsTimes.get_format_utc_8()}]\n{message}"
        text = text.translate(str.maketrans({
            c: f'\\{c}' for c in '_[]()~>#+-=|{}.!'
        }))
        cmd = (f"""curl -k """
               f"""--data-urlencode chat_id='{chat_id}' """
               f"""--data-urlencode parse_mode='MarkdownV2' """
               f"""--data-urlencode 'text=*机器人通知消息*\n{text}' """
               f"""'https://api.telegram.org/bot{token}/sendMessage' """)

        os.system(cmd)


async def main():
    """

    :return:
    """
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