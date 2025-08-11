#! /bin/bash


# 设置默认值
default_url="https://fastly.jsdelivr.net/gh/Alvin9999/pac2@latest/singbox/config.json"
default_port=1080


url="${1:-$default_url}"
port="${2:-$default_port}"

echo "url=$url"
echo "port=$port"

# 启动前准备
cd /etc/sing-box
rm -rf *.log
pkill -f sing-box

# 下载订阅链接内容
rm config.json
touch config.json
curl -o ./config.json $url

# 修改启动的代理端口
# sed -i "s/1080/$port/g" ./config.json
sed -i 's/"listen_port": [0-9]\+/"listen_port": '"$port"'/g' ./config.json

#  启动sing-box
./sing-box run -c config.json
