#! /bin/bash


# 设置默认值
default_url="https://fastly.jsdelivr.net/gh/Alvin9999/pac2@latest/singbox/config.json"
default_port=1080
proxy=""


url="${1:-$default_url}"
port="${2:-$default_port}"
proxy="${3:-$proxy}"

echo "url=$url"
echo "port=$port"
echo "proxy=$proxy"

# 启动前准备
cd /etc/sing-box
rm -rf *.log
pkill -f sing-box

# 下载订阅链接内容
rm config.json
touch config.json

if [ ! -z "$proxy" ]; then
  echo "使用代理: $proxy"
  curl -o ./config.json $url -x "$proxy"
else
  echo "不使用代理"
  curl -o ./config.json $url
fi

# 修改启动的代理端口
sed -i 's/"listen_port": [0-9]\+/"listen_port": '"$port"'/g' ./config.json

#  启动sing-box
./sing-box run -c config.json
