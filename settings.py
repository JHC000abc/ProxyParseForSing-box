PROXY_HOST = "192.168.2.109"
PROXY_PORT = 10808

# aiohttp 使用的代理(主要用于请求github等地址使用 程序中通过配置 self.infos 中的 proxy 确定是否启用)
PROXIES_ASYNC = f"http://{PROXY_HOST}:{PROXY_PORT}"
# PROXIES_ASYNC = None


SING_BOX_PATH = "plugins/sing-box"
UPLOAD_TOOLS_FILE = "plugins/upload"
TELEGRAM_TOOLS_FILE = "plugins/telegram"

# 最后输出的订阅节点默认的测试端口
OUT_LISTEN_PORT = 1080

# 异步测试时使用的测试端口 默认的(只能支持同时测试一个，程序中用了自增的端口号，这个用不到了)
TEST_LISTEN_PORT = 10800

# 最大延迟(单位ms, 测速结果大于此值的不做保留)
SPEED_LIMIT = 1000
