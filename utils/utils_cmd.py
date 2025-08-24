import asyncio


class AsyncCMD:
    """

    """

    async def run_cmd_async(self, cmd: str):
        """

        :param cmd:
        :return:
        """
        proc = await asyncio.create_subprocess_exec(
            *cmd.split(),  # Safer than shell=True
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT
        )

        try:
            while True:
                line = await proc.stdout.readline()
                if not line:
                    break
                yield line.decode('utf-8').strip(), proc
        finally:
            if proc.returncode is None:
                proc.terminate()
                try:
                    await asyncio.wait_for(proc.wait(), timeout=5)
                except asyncio.TimeoutError:
                    proc.kill()
                    print("Forced termination of subprocess.")
