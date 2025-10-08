import traceback
import asyncio
import random
from functools import wraps
from settings.setting import NEWTWORK_RETRY_TIMES


def retry(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        flag = False
        retry_times = NEWTWORK_RETRY_TIMES
        while not flag and retry_times > 0:
            try:
                res = await func(*args, **kwargs)
                flag = True
                return res
            except Exception as e:
                print(traceback.format_exc())
            finally:
                retry_times -= 1
                await asyncio.sleep(random.randint(1, 3))

        print(f"函数 '{func.__name__}' 在 5 次尝试后仍失败。{args}{kwargs}")
        raise

    return wrapper
