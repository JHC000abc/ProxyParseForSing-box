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

or 远程仓库拉取

```bash
  docker pull jhc0000abc/sing-box-v1.8.8-rule:latest
```

测试命令：

```bash
  docker run -it --name=sing-box-test -p 10809:1080 --rm --entrypoint="/etc/sing-box/restart.sh" jhc0000abc/sing-box-v1.8.8-rule:latest "CDN链接"
```

启动命令：

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

# 环境恢复：

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
    uv run get_latest_CDN.py
```









