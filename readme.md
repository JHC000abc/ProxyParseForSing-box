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

## V2 版本的 不需要启动参数 使用 limestart 里的便签存储 url (只要 limestart token 不过期 重启后获取的就是 Github Action 每两小时生成的最新链接，稳定不稳定再说吧，自己没服务器，白嫖一下别人的)

```bash
  docker run -itd --name=sing-box -p 10808:1080 --restart=always --entrypoint="/etc/sing-box/restart.sh" jhc0000abc/sing-box-1.8.8-v2:latest
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

## 4. 项目整体打包成可执行文件

```bash
     pyarmor gen -r --pack FC main.py && cp dist/main ./ && rm -rf dist/ .pyarmor/ main.spec
```

## 5. 打包telegram 工具(自行添加代码中的 token 和 id )

```bash
  pyarmor gen -r --pack FC tools/tools_telegram.py && mv dist/tools_telegram plugins/telegram && rm -rf dist/ .pyarmor/ utils_telegram.spec
```

## 6. 打包转手机订阅链接插件

```bash
    pyarmor gen -r --pack FC tools/tools_trans_phone.py && mv dist/tools_trans_phone plugins/trans_phone && rm -rf dist/ .pyarmor/ tools_trans_phone.spec
```

## 7. 打包 limestart 存储工具

```bash
    pyarmor gen -r --pack FC tools/tools_limestart.py && mv dist/tools_limestart plugins/limestart && rm -rf dist/ .pyarmor/ tools_limestart.spec
```

## 8. 打包 limestart 存储工具 获取最新url

```bash
    pyarmor gen -r --pack FC tools/tools_limestart.py && mv dist/tools_limestart plugins/get_latest_url && rm -rf dist/ .pyarmor/ tools_limestart.spec
```

## 9. 打包 limestart 清理工具 获取最新url

```bash
    pyarmor gen -r --pack FC tools/tools_limestart.py && mv dist/tools_limestart plugins/clear_old_url && rm -rf dist/ .pyarmor/ tools_limestart.spec
```

## 10. 打包 CDN 获取 工具 获取最新 提交的文件对应的 CDN 链接

```bash
    pyarmor gen -r --pack FC tools/tools_gen_latest_CDN.py && mv dist/tools_gen_latest_CDN plugins/gen_latest_CDN && rm -rf dist/ .pyarmor/ tools_gen_latest_CDN.spec
```

## 11. git push 提交 新生成的json文件 到github仓库

## 12. 获取新上传json 文件对应的CDN链接

```bash
    ./plugins/gen_latest_CDN
```

# 错误提示

1. 找不到项目中的文件夹：在项目根路径下执行

```bash
  export PYTHONPATH=$PYTHONPATH:$PWD 
```

# 目前支持解析的协议：

* trojan
* hysteria2
* vless
* vmess
* shadowsocks

# 致谢

## 内置节点订阅：

### 所有节点均来自 github，开源的，不对安全性作任何保证，慎用，

### 具体哪来的我也忘记了，但是在此鸣谢各位大佬

* https://raw.githubusercontent.com/snakem982/proxypool/main/source/v2ray-2.txt
* https://a.nodeshare.xyz/uploads/2025/7/20250720.txt
* https://github.com/sharkDoor/vpn-free-nodes/tree/master/node-list/
* https://github.com/vpnmianfei/vpnmianfei.github.io 或者 https://github.com/pcfreevpn/pcfreevpn.github.io
* https://github.com/Barabama/FreeNodes

# [第一次录制的参考视频 用的1.0版本 仅供参考](https://www.youtube.com/watch?v=yRuacjm3zt4)

## 白嫖的大佬写的便签接口用来存储 url 特此致谢

[青柠起始页](https://www.limestart.cn/) 这项目相当不错,很好用,标签页,便签,空投快传 都很好用 感兴趣的可以注册个账号试一下

# 环境说明

1. 本项目运行在Docker环境中
2. 基础镜像使用的是官方的 ubuntu:22.04 最新版本的镜像
3. 内置了 sing-box 1.8.8 版本
4. Python 版本 >=3.9.9
5. 使用GitHub Actions 每2小时抓取并推送最新节点数据
6.

# 更新记录

2025.08.24

1. 调整项目结构
2. 内置订阅节点调整到三个
3. 5种协议增加特殊情况处理
4. 全面采用异步结构，增加处理速度
5. 先统一获取订阅内容，再统一异步多线程测速
6. 增加默认节点上传位置为BOS，避免CDN有时无法访问问题(uv run main.py 最后输出的url就是，可以替代CDN链接使用)
7. ParseNodesharkDoor 默认处理今天所有的节点信息

2025.08.25

1. 增加Telegram
   机器人自动向用户推送节点信息[自行通过BotFather 创建机器人，获取Token ,以及id](https://longnight.github.io/2018/12/12/Telegram-Bot-notifications)
2. 增加 GitHub Actions 每天 8-19 点 每小时推送一次最新抓取的节点信息到指定id下
3. 解决 GitHub Actions 上无法运行 plugins/telegram plugins/upload 问题 (原因：本机和GitHub
   Actions的Ubuntu版本不一致，解决：在Docker里打包个版本一致的可执行文件)
4. 增加项目打包,简化 GitHub Actions 构建过程 直接执行可知性文件即可
5. 增加节点转手机 sing-box 专用订阅工具 (手机端无法使用规则，只能直连)

2025.08.26

1. 增加 limestart 存储工具，获取最新url
2. 增加 V2.0 版本镜像 jhc0000abc/sing-box-1.8.8-v2:latest 使用 limestart 存储工具
3. 优化项目结构,把网络请求部分单独提出来到 utils/ 下
4. 打包 gen_latest_CDN 为可执行工具

2025.08.27

1. 增加删除 limestart 存储记录工具,只保留最新一条
2. 添加手机端sing-box配置文件模板
3. 增加节点订阅源
4. 优化节点解析规则
4. 优化并发测速,限制并发量
5. 增加不解析的国家/区域 forbidden_areas.list


2025.08.28

1. 使用GitHub Actions 每1小时抓取并推送最新节点数据
2. 优化项目结构


2025.08.31

1. 增加节点订阅源
2. 增加正则过滤ip 规则


2025.09.01

1. 优化节点数量，取消抓取成功率较低的节点
2. 增加地区限制,保证代理可用于 https://gemini.google.com/
3. 项目基本完成，如无长时间无法不获取新节点情况出现，不再修改

