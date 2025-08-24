# 这部分是把容器打包成镜像，使用网络拉取可忽略

sing-box 代理 实现在docker中开启服务，本机浏览器直连代理实现科学上网(内置节点)

镜像包名：sing-box-v1.8.8-rule.tar

proxy.list:订阅地址文件（所有订阅地址均来自于github 开源项目 ChromeGo）

提交已经修改好的容器（正在运行的容器）：

```bash
  docker commit <container_id> <new_image_name>:<tag>
```

打包命令：

```bash 
  docker save -o sing-box-v1.8.8-rule.tar sing-box-v1.8.8-rule:latest
```

加载命令：切换到 sing-box-v1.8.8-rule.tar 所在文件夹中 cmd运行

```bash
  docker load -i sing-box-v1.8.8-rule.tar
```

# 这里是常规用户使用流程

or 远程仓库拉取

```bash
  docker pull jhc0000abc/sing-box-v1.8.8-rule:latest
```

测试命令：

```bash
  docker run -it --name=sing-box-test -p 10809:1080 --rm --entrypoint="/etc/sing-box/restart.sh" jhc0000abc/sing-box-v1.8.8-rule:latest "CDN链接"
```

启动命令：
docker run -itd --name=sing-box -p 10808:1080 --restart=always --entrypoint="/etc/sing-box/restart.sh"
jhc0000abc/sing-box-v1.8.8-rule:latest "CDN链接" "1080" "下载CDN链接的代理（curl 用的）"

## 使用代理下载CDN

```bash
  docker run -itd --name=sing-box -p 10808:1080 --restart=always --entrypoint="/etc/sing-box/restart.sh" jhc0000abc/sing-box-v1.8.8-rule:latest "CDN链接" "1080" "192.168.2.109:10809"  
```

## 不使用代理下载CDN

```bash
  docker run -itd --name=sing-box -p 10808:1080 --restart=always --entrypoint="/etc/sing-box/restart.sh" jhc0000abc/sing-box-v1.8.8-rule:latest "CDN链接" "1080" 
```

Windows系统 Chrome 浏览器启动命令（需要先把chrome.exe目录配置到环境变量中，启动前关闭所有chrome浏览器窗口）：

```bash
  chrome.exe --user-data-dir="xxx" --proxy-server="socks5://127.0.0.1:10808"  https://limestart.cn/
```

至此chrome浏览器可以科学上网了

其它软件也可以通过本机 http://127.0.0.1:10808 实现科学上网

```json lines
    proxies = {
    "http": "http://127.0.0.1:10808",
    "https": "http://127.0.0.1:10808",
}
```

# 上传镜像

```bash
    docker login
    docker tag <本地镜像名> <目标仓库地址>/<用户名>/<镜像名>:<版本号>
    docker push <你打好的标签>
```

# 环境恢复（这里获取CDN链接）：

## 1. 安装uv

```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 2. 同步脚本运行环境

```bash
    uv sync
```

## 3. 转换代理

```bash
uv run main.py
```

## 4. git push 提交 新生成的json文件 到github仓库

## 5. 获取新上传json 文件对应的CDN链接

```bash
    uv run gen_latest_CDN.py
```

# 目前支持解析的协议：

* trojan
* hysteria2
* vless
* vmess
* shadowsocks

# 内置节点订阅：

## （所有节点均来自 github，开源的，不对安全性作任何保证，慎用，具体哪来的我也忘记了，但是在此鸣谢各位大佬）

* https://raw.githubusercontent.com/snakem982/proxypool/main/source/v2ray-2.txt
* https://a.nodeshare.xyz/uploads/2025/7/20250720.txt
* https://github.com/sharkDoor/vpn-free-nodes/tree/master/node-list/

# [第一次录制的视频 有点low 仅供参考](https://www.youtube.com/watch?v=yRuacjm3zt4)

# 更新记录

2025.08.24

1. 调整项目结构
2. 内置订阅节点调整到三个
3. 5种协议增加特殊情况处理
4. 全面采用异步结构，增加处理速度
5. 先统一获取订阅内容，再统一异步多线程测速
6. 增加默认节点上传位置为BOS，避免CDN有时无法访问问题(uv run main.py 最后输出的url就是，可以替代CDN链接使用)
7. ParseNodesharkDoor 默认处理今天所有的节点信息
8. 



