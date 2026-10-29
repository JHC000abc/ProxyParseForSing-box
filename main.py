#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ProxyParseForSing-box - main.py

将 Clash YAML 订阅 / 传统 URI 订阅解析为 sing-box 配置。
支持协议：http, socks5, anytls, vmess, vless, trojan, hysteria2, ss

用法:
    uv run main.py                                  # 使用默认订阅 URL
    uv run main.py --url "https://..."              # 指定订阅 URL
    uv run main.py --file "port 7890.txt"           # 从本地 Clash 文件读取
    uv run main.py --port 1080 -o config.json       # 自定义入站端口 / 输出文件
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import urllib.parse
from typing import Any

import requests
import yaml


# ============================================================
# 默认配置
# ============================================================

DEFAULT_URL = "https://sub.danhu.dpdns.org/paste/TG@FProxies261024fhU8Dbp/clash"
DEFAULT_LISTEN_PORT = 1080
DEFAULT_OUTPUT = "config.json"
DEFAULT_TEST_URL = "https://www.gstatic.com/generate_204"


# ============================================================
# 通用工具函数
# ============================================================

def _clean(v: Any) -> str | None:
    """过滤 None / 'null' / 'None' / 'undefined' / 空串（大小写不敏感）。"""
    if v is None:
        return None
    if not isinstance(v, str):
        return str(v)
    s = v.strip()
    if not s or s.lower() in {"null", "none", "undefined"}:
        return None
    return v


def _tls(proxy: dict, *, force: bool = False, reality: bool = False) -> dict | None:
    """将 Clash 的 tls/sni/skip-cert-verify 映射为 sing-box tls 块。"""
    if not force and not proxy.get("tls"):
        return None

    tls: dict[str, Any] = {"enabled": True}

    sni = _clean(proxy.get("sni")) or _clean(proxy.get("servername"))
    if sni:
        tls["server_name"] = sni

    if reality:
        ro = proxy.get("reality-opts") or {}
        if ro.get("public-key"):
            tls["reality"] = {
                "enabled": True,
                "public_key": ro["public-key"],
                "short_id": ro.get("short-id") or "",
            }
        # reality 场景不设置 insecure
    else:
        if proxy.get("skip-cert-verify"):
            tls["insecure"] = True

    fp = _clean(proxy.get("client-fingerprint"))
    if fp:
        tls["utls"] = {"enabled": True, "fingerprint": fp}

    return tls


def _transport(proxy: dict) -> dict | None:
    """将 Clash 的 ws-opts / grpc-opts 映射为 sing-box transport 块。"""
    net = proxy.get("network")

    if net == "ws":
        ws = proxy.get("ws-opts") or {}
        t: dict[str, Any] = {"type": "ws"}
        if ws.get("path"):
            t["path"] = ws["path"]
        if ws.get("headers"):
            t["headers"] = {k: str(v) for k, v in ws["headers"].items()}
        return t

    if net == "grpc":
        grpc = proxy.get("grpc-opts") or {}
        t = {"type": "grpc"}
        if grpc.get("grpc-service-name"):
            t["service_name"] = grpc["grpc-service-name"]
        return t

    return None


# ============================================================
# Clash YAML -> sing-box outbound
# ============================================================

def _to_http(p: dict) -> dict:
    ob: dict[str, Any] = {
        "type": "http",
        "tag": p["name"],
        "server": p["server"],
        "server_port": int(p["port"]),
    }
    if u := _clean(p.get("username")):
        ob["username"] = u
    if w := _clean(p.get("password")):
        ob["password"] = w
    if t := _tls(p):
        ob["tls"] = t
    return ob


def _to_socks(p: dict) -> dict:
    ob: dict[str, Any] = {
        "type": "socks",
        "tag": p["name"],
        "server": p["server"],
        "server_port": int(p["port"]),
        "version": "5",
    }
    if u := _clean(p.get("username")):
        ob["username"] = u
    if w := _clean(p.get("password")):
        ob["password"] = w
    return ob


def _to_anytls(p: dict) -> dict:
    ob: dict[str, Any] = {
        "type": "anytls",
        "tag": p["name"],
        "server": p["server"],
        "server_port": int(p["port"]),
        "password": p["password"],
        "tls": _tls(p, force=True) or {"enabled": True},
    }
    return ob


def _to_vmess(p: dict) -> dict:
    ob: dict[str, Any] = {
        "type": "vmess",
        "tag": p["name"],
        "server": p["server"],
        "server_port": int(p["port"]),
        "uuid": p["uuid"],
        "security": p.get("cipher", "auto"),
        "alter_id": int(p.get("alterId", 0) or 0),
    }
    if t := _tls(p):
        ob["tls"] = t
    if tr := _transport(p):
        ob["transport"] = tr
    return ob


def _to_vless(p: dict) -> dict:
    has_reality = bool((p.get("reality-opts") or {}).get("public-key"))
    ob: dict[str, Any] = {
        "type": "vless",
        "tag": p["name"],
        "server": p["server"],
        "server_port": int(p["port"]),
        "uuid": p["uuid"],
    }
    if flow := _clean(p.get("flow")):
        ob["flow"] = flow
    if t := _tls(p, reality=has_reality):
        ob["tls"] = t
    if tr := _transport(p):
        ob["transport"] = tr
    return ob


def _to_trojan(p: dict) -> dict:
    ob: dict[str, Any] = {
        "type": "trojan",
        "tag": p["name"],
        "server": p["server"],
        "server_port": int(p["port"]),
        "password": p["password"],
        "tls": _tls(p, force=True) or {"enabled": True},
    }
    if tr := _transport(p):
        ob["transport"] = tr
    return ob


def _to_hysteria2(p: dict) -> dict:
    ob: dict[str, Any] = {
        "type": "hysteria2",
        "tag": p["name"],
        "server": p["server"],
        "server_port": int(p["port"]),
        "password": p.get("password") or p.get("auth"),
        "tls": {"enabled": True},
    }
    if p.get("skip-cert-verify"):
        ob["tls"]["insecure"] = True
    if sni := _clean(p.get("sni")) or _clean(p.get("servername")):
        ob["tls"]["server_name"] = sni
    if obfs := p.get("obfs"):
        ob["obfs"] = {"type": obfs, "password": p.get("obfs-password", "")}
    return ob


def _to_ss(p: dict) -> dict:
    return {
        "type": "shadowsocks",
        "tag": p["name"],
        "server": p["server"],
        "server_port": int(p["port"]),
        "method": p["cipher"],
        "password": p["password"],
    }


CLASH_MAPPERS = {
    "http": _to_http,
    "socks5": _to_socks,
    "anytls": _to_anytls,
    "vmess": _to_vmess,
    "vless": _to_vless,
    "trojan": _to_trojan,
    "hysteria2": _to_hysteria2,
    "ss": _to_ss,
}


def clash_proxy_to_singbox(proxy: dict) -> dict | None:
    mapper = CLASH_MAPPERS.get(proxy.get("type"))
    if not mapper:
        return None
    try:
        return mapper(proxy)
    except Exception as e:
        print(f"[skip] {proxy.get('name')}: {e}", file=sys.stderr)
        return None


def parse_clash_yaml(text: str) -> list[dict]:
    cfg = yaml.safe_load(text)
    if not isinstance(cfg, dict) or "proxies" not in cfg:
        return []
    return _convert_proxy_list(cfg.get("proxies") or [])


# ============================================================
# 传统 URI 订阅 -> sing-box outbound
# ============================================================

def _b64decode(s: str) -> str:
    s = s.strip().replace("-", "+").replace("_", "/")
    pad = "=" * (-len(s) % 4)
    return base64.b64decode(s + pad).decode("utf-8", errors="ignore")


def _uri_tls(params: dict, reality: bool = False) -> dict | None:
    security = params.get("security", "").lower()
    if security not in {"tls", "reality", "xtls"} and not reality:
        if params.get("tls") not in ("1", "true", "True"):
            return None
    tls: dict[str, Any] = {"enabled": True}
    if sni := params.get("sni") or params.get("peer"):
        tls["server_name"] = sni
    if params.get("allowInsecure") in ("1", "true", "True") or params.get("insecure") in ("1", "true", "True"):
        tls["insecure"] = True
    if security == "reality" or reality:
        pbk = params.get("pbk")
        if pbk:
            tls["reality"] = {
                "enabled": True,
                "public_key": pbk,
                "short_id": params.get("sid") or "",
            }
    if fp := params.get("fp"):
        tls["utls"] = {"enabled": True, "fingerprint": fp}
    return tls


def _uri_transport(params: dict) -> dict | None:
    net = params.get("type", "tcp").lower()
    if net == "ws":
        t: dict[str, Any] = {"type": "ws"}
        if path := params.get("path"):
            t["path"] = urllib.parse.unquote(path)
        host = params.get("host")
        if host:
            t["headers"] = {"Host": host}
        return t
    if net == "grpc":
        t = {"type": "grpc"}
        if sn := params.get("serviceName"):
            t["service_name"] = sn
        return t
    if net == "httpupgrade":
        t = {"type": "httpupgrade"}
        if path := params.get("path"):
            t["path"] = path
        if host := params.get("host"):
            t["host"] = host
        return t
    return None


def _parse_vmess_uri(uri: str) -> dict | None:
    try:
        raw = _b64decode(uri[8:])
        obj = json.loads(raw)
    except Exception:
        return None
    params = {
        "sni": obj.get("sni") or obj.get("host", ""),
        "type": obj.get("net", "tcp"),
        "path": obj.get("path", ""),
        "host": obj.get("host", ""),
        "security": obj.get("tls", ""),
        "fp": obj.get("fp", ""),
    }
    ob: dict[str, Any] = {
        "type": "vmess",
        "tag": obj.get("ps") or f"vmess-{obj.get('add')}",
        "server": obj.get("add"),
        "server_port": int(obj.get("port")),
        "uuid": obj.get("id"),
        "security": obj.get("scy", "auto") or "auto",
        "alter_id": int(obj.get("aid", 0) or 0),
    }
    if obj.get("tls"):
        if t := _uri_tls({"security": "tls", "sni": params["sni"]}):
            ob["tls"] = t
    if tr := _uri_transport(params):
        ob["transport"] = tr
    return ob


def _parse_standard_uri(uri: str, scheme: str) -> dict | None:
    parsed = urllib.parse.urlparse(uri)
    params = dict(urllib.parse.parse_qsl(parsed.query, keep_blank_values=True))
    name = urllib.parse.unquote(parsed.fragment) or f"{scheme}-{parsed.hostname}"
    host = parsed.hostname
    port = parsed.port or (443 if scheme in ("trojan", "hysteria2") else 80)

    if scheme == "vless":
        ob: dict[str, Any] = {
            "type": "vless",
            "tag": name,
            "server": host,
            "server_port": port,
            "uuid": parsed.username,
        }
        if flow := params.get("flow"):
            ob["flow"] = flow
        if t := _uri_tls(params, reality=params.get("security", "").lower() == "reality"):
            ob["tls"] = t
        if tr := _uri_transport(params):
            ob["transport"] = tr
        return ob

    if scheme == "trojan":
        ob = {
            "type": "trojan",
            "tag": name,
            "server": host,
            "server_port": port,
            "password": parsed.username,
            "tls": _uri_tls(params, reality=False) or {"enabled": True, "insecure": params.get("allowInsecure") in ("1", "true", "True")},
        }
        if tr := _uri_transport(params):
            ob["transport"] = tr
        return ob

    if scheme in ("hysteria2", "hy2"):
        tls: dict[str, Any] = {"enabled": True}
        if sni := params.get("sni"):
            tls["server_name"] = sni
        if params.get("insecure") in ("1", "true", "True"):
            tls["insecure"] = True
        ob = {
            "type": "hysteria2",
            "tag": name,
            "server": host,
            "server_port": port,
            "password": parsed.username or params.get("password", ""),
            "tls": tls,
        }
        if obfs := params.get("obfs"):
            ob["obfs"] = {"type": obfs, "password": params.get("obfs-password", "")}
        return ob

    return None


def _parse_ss_uri(uri: str) -> dict | None:
    body = uri[5:]
    name = ""
    if "#" in body:
        body, name = body.split("#", 1)
        name = urllib.parse.unquote(name)
    if "@" in body:
        userinfo, hostport = body.rsplit("@", 1)
        try:
            decoded = _b64decode(userinfo)
            if ":" in decoded:
                method, password = decoded.split(":", 1)
            else:
                method, password = userinfo.split(":", 1)
        except Exception:
            method, password = userinfo.split(":", 1)
    else:
        try:
            decoded = _b64decode(body)
        except Exception:
            return None
        if "@" not in decoded:
            return None
        userinfo, hostport = decoded.rsplit("@", 1)
        method, password = userinfo.split(":", 1)

    hostport = hostport.split("?")[0]
    if ":" not in hostport:
        return None
    host, port = hostport.rsplit(":", 1)
    return {
        "type": "shadowsocks",
        "tag": name or f"ss-{host}",
        "server": host,
        "server_port": int(port),
        "method": method,
        "password": password,
    }


def parse_uri_list(text: str) -> list[dict]:
    uris = [line.strip() for line in text.splitlines() if line.strip()]
    outbounds: list[dict] = []
    for uri in uris:
        try:
            scheme = uri.split("://", 1)[0].lower()
            if scheme == "vmess":
                ob = _parse_vmess_uri(uri)
            elif scheme in {"vless", "trojan", "hysteria2", "hy2"}:
                ob = _parse_standard_uri(uri, scheme)
            elif scheme == "ss":
                ob = _parse_ss_uri(uri)
            else:
                ob = None
            if ob:
                outbounds.append(ob)
        except Exception as e:
            print(f"[skip] {uri[:40]}...: {e}", file=sys.stderr)
    return outbounds


# ============================================================
# 订阅获取 & 自动识别
# ============================================================

def load_subscription_text(url: str | None = None, file: str | None = None) -> str:
    if file:
        with open(file, "r", encoding="utf-8") as f:
            return f.read()
    if not url:
        raise ValueError("必须提供 url 或 file")
    resp = requests.get(url, timeout=30, headers={"User-Agent": "sing-box/1.8.8"})
    resp.raise_for_status()
    return resp.text


def detect_and_parse(text: str) -> list[dict]:
    """自动识别 Clash YAML 或 base64/明文 URI 订阅。"""
    stripped = text.strip()

    # 1) 尝试 Clash YAML
    if stripped.startswith(("proxies:", "port:", "socks-port:", "mixed-port:")):
        return parse_clash_yaml(stripped)

    # 2) 尝试 base64 解码后再判断
    try:
        decoded = _b64decode(stripped)
        if "://" in decoded:
            return parse_uri_list(decoded)
    except Exception:
        pass

    # 3) 明文 URI 列表
    if "://" in stripped:
        return parse_uri_list(stripped)

    # 4) 最后再试一次 YAML
    return parse_clash_yaml(stripped)


# ============================================================
# 输出 sing-box 配置
# ============================================================

def _dedup_tags(outbounds: list[dict]) -> list[dict]:
    seen: dict[str, int] = {}
    for ob in outbounds:
        tag = ob["tag"]
        if tag in seen:
            seen[tag] += 1
            ob["tag"] = f"{tag} ({seen[tag]})"
        else:
            seen[tag] = 0
    return outbounds


def build_singbox_config(outbounds: list[dict], listen_port: int = DEFAULT_LISTEN_PORT) -> dict:
    tags = [ob["tag"] for ob in outbounds]

    proxy_group: dict[str, Any] = {
        "type": "selector",
        "tag": "proxy",
        "outbounds": (["auto"] if tags else ["direct"]) + tags,
        "default": "auto" if tags else "direct",
    }

    config: dict[str, Any] = {
        "log": {"level": "info", "timestamp": True},
        "inbounds": [
            {
                "type": "mixed",
                "tag": "mixed-in",
                "listen": "::",
                "listen_port": listen_port,
            }
        ],
        "outbounds": [proxy_group],
        "route": {
            "rules": [],
            "final": "proxy",
            "auto_detect_interface": True,
        },
    }

    if tags:
        config["outbounds"].append({
            "type": "urltest",
            "tag": "auto",
            "outbounds": tags,
            "url": DEFAULT_TEST_URL,
            "interval": "5m",
            "tolerance": 50,
        })

    config["outbounds"].append({"type": "direct", "tag": "direct"})
    config["outbounds"].extend(outbounds)

    return config


# ============================================================
# 入口
# ============================================================

def main() -> int:
    parser = argparse.ArgumentParser(description="Clash / URI 订阅 -> sing-box 配置")
    parser.add_argument("--url", default=os.getenv("SUB_URL", DEFAULT_URL), help="订阅 URL")
    parser.add_argument("--file", default=None, help="本地 Clash YAML 文件路径（优先于 --url）")
    parser.add_argument("--port", type=int, default=DEFAULT_LISTEN_PORT, help="mixed 入站端口")
    parser.add_argument("-o", "--output", default=DEFAULT_OUTPUT, help="输出文件名")
    args = parser.parse_args()

    try:
        text = load_subscription_text(url=None if args.file else args.url, file=args.file)
    except Exception as e:
        print(f"[error] 获取订阅失败: {e}", file=sys.stderr)
        return 1

    outbounds = _dedup_tags(detect_and_parse(text))
    if not outbounds:
        print("[error] 未解析到任何节点", file=sys.stderr)
        return 1

    config = build_singbox_config(outbounds, listen_port=args.port)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    print(f"[ok] 解析到 {len(outbounds)} 个节点 -> {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
