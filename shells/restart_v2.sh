#! /bin/bash

# 不支持任何输入 直接从 limestart 获取最新的 url jhc0000abc/sing-box-1.8.8-v2:latest

port=1080

# 启动前准备
cd /etc/sing-box
rm -rf *.log
pkill -f sing-box

# 下载订阅链接内容
rm config.json | true
touch config.json

./get_latest_url | xargs curl -o config.json

# 修改启动的代理端口
sed -i 's/"listen_port": [0-9]\+/"listen_port": '"$port"'/g' ./config.json

#  启动sing-box
./sing-box run -c config.json
