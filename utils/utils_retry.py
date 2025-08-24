import traceback
import asyncio
import random
from functools import wraps


def retry(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        flag = False
        retry_times = 5
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

        raise Exception(f"函数 '{func.__name__}' 在 5 次尝试后仍失败。")

    return wrapper
