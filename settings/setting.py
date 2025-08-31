DEBUG = False

if DEBUG:
    PROXY_HOST = "192.168.2.109"
    PROXY_PORT = 10808
    # 代理
    PROXIES_ASYNC = f"http://{PROXY_HOST}:{PROXY_PORT}"
else:
    # 代理
    PROXIES_ASYNC = None



# sing-box 工具
SING_BOX_PATH = "plugins/sing-box"
# 公网订阅链接生成工具
UPLOAD_TOOLS_FILE = "plugins/upload"
# TG 机器人通知工具
TELEGRAM_TOOLS_FILE = "plugins/telegram"
# 节点转换手机版工具
TRANS_PHONE_TOOLS_FILE = "plugins/trans_phone"
# limestart 上传工具路径
LIMESTART_TOOLS_FILE = "plugins/limestart"

# 排除区域
FORBIDDEN_AREA_FILE = "files/forbidden_areas.list"
# 排除server
FORBIDDEN_PROXY_FILE = "files/frobidden_proxy.list"
# 正则排除server 规则
FORBIDDEN_SERVER_RE_FILE = "files/forbidden_server_re.list"

# 最后输出的订阅节点默认的测试端口
OUT_LISTEN_PORT = 1080

# 节点在sing-box中测速更新间隔时长
UPDATE_NODES_TIMES = "5m"

# 网络请求超时时间
TIMEOUT = 10

# 单次最大并法测速数量
MAX_CONCURRENCY = 100

# 获取节点地区网站
TEST_IP_NODE = "cip.cc"

# 异步测试时使用的测试端口 默认的(只能支持同时测试一个，程序中用了自增的端口号，这个用不到了)
TEST_LISTEN_PORT = 10900

# 最大延迟(单位ms, 测速结果大于此值的不做保留)
SPEED_LIMIT = 2000

# 节点测速网址
NODE_TEST_CONNECT_SPEED = "https://gemini.google.com/gem"
# NODE_TEST_CONNECT_SPEED = "https://speed.cloudflare.com/_-down?bytes=100000000"
# NODE_TEST_CONNECT_SPEED = "https://www.google.com/generate_204"
