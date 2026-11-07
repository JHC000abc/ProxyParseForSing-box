# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@author: JHC000abc@gmail.com
@file: tool_gen_tmp_bos.py
@time: 2026/11/7 22:53 
@desc: 

"""
import sys
import os
import re
import json
import time
import base64
import hashlib
import hmac
import random
import string
from datetime import datetime, timezone
from urllib.parse import quote

import requests

# ==================== 固定配置 ====================
BASE_HOST = "aisearch.bj.bcebos.com"
IS_PRIVATE_CHAT = False
EXPIRE_SEC = -1

TOKEN_LID_URL = "https://wenxin.baidu.com/search/10505248536417466602?enter_type=pic_picedit"
STS_URL      = "https://chat.baidu.com/aichat/api/file/sts"
REGISTER_URL = "https://chat.baidu.com/aichat/api/file/upload"

TOKEN_CACHE_TTL = 5 * 60  # token/lid 本地缓存 5 分钟
DEBUG = os.environ.get("WENXIN_DEBUG") == "1"


def log(msg: str):
    """调试日志 → stderr，默认静默；Typora 不会看到。"""
    if DEBUG:
        print(msg, file=sys.stderr, flush=True)


# ==================== HTTP ====================
SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
})


# ==================== 本地缓存 ====================
def _cache_dir() -> str:
    base = os.environ.get("XDG_CACHE_HOME") or os.path.expanduser("~/.cache")
    return os.path.join(base, "wenxin-upload")


def _token_cache_file() -> str:
    return os.path.join(_cache_dir(), "token_lid.json")


def load_cached_token():
    try:
        with open(_token_cache_file(), "r", encoding="utf-8") as f:
            data = json.load(f)
        if float(data.get("expireAt", 0)) > time.time():
            if data.get("token") and data.get("lid"):
                return data["token"], data["lid"]
    except Exception:
        pass
    return None


def save_cached_token(token: str, lid: str):
    try:
        os.makedirs(_cache_dir(), exist_ok=True)
        with open(_token_cache_file(), "w", encoding="utf-8") as f:
            json.dump(
                {"token": token, "lid": lid, "expireAt": time.time() + TOKEN_CACHE_TTL},
                f,
            )
    except Exception:
        pass


def clear_cached_token():
    try:
        os.remove(_token_cache_file())
    except Exception:
        pass


# ==================== MIME 映射（与 JS MIME_MAP 对齐） ====================
# ext -> (contentType, bizType)
MIME_MAP = {
    # ---- image ----
    "png":  ("image/png", "image"),
    "jpg":  ("image/jpeg", "image"),
    "jpeg": ("image/jpeg", "image"),
    "gif":  ("image/gif", "image"),
    "webp": ("image/webp", "image"),
    "bmp":  ("image/bmp", "image"),
    "svg":  ("image/svg+xml", "image"),
    "ico":  ("image/x-icon", "image"),
    "tif":  ("image/tiff", "image"),
    "tiff": ("image/tiff", "image"),
    # ---- video ----
    "mp4":  ("video/mp4", "video"),
    "mov":  ("video/quicktime", "video"),
    "avi":  ("video/x-msvideo", "video"),
    "mkv":  ("video/x-matroska", "video"),
    "webm": ("video/webm", "video"),
    "flv":  ("video/x-flv", "video"),
    "wmv":  ("video/x-ms-wmv", "video"),
    "m4v":  ("video/x-m4v", "video"),
    "3gp":  ("video/3gpp", "video"),
    "mpeg": ("video/mpeg", "video"),
    "mpg":  ("video/mpeg", "video"),
    # ---- audio ----
    "mp3":  ("audio/mpeg", "audio"),
    "wav":  ("audio/wav", "audio"),
    "m4a":  ("audio/mp4", "audio"),
    "aac":  ("audio/aac", "audio"),
    "flac": ("audio/flac", "audio"),
    "ogg":  ("audio/ogg", "audio"),
    "wma":  ("audio/x-ms-wma", "audio"),
    # ---- file ----
    "pdf":  ("application/pdf", "file"),
    "xlsx": ("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "file"),
    "xls":  ("application/vnd.ms-excel", "file"),
    "csv":  ("text/csv", "file"),
    "docx": ("application/vnd.openxmlformats-officedocument.wordprocessingml.document", "file"),
    "doc":  ("application/msword", "file"),
    "pptx": ("application/vnd.openxmlformats-officedocument.presentationml.presentation", "file"),
    "ppt":  ("application/vnd.ms-powerpoint", "file"),
    "txt":  ("text/plain", "file"),
    "md":   ("text/markdown", "file"),
    "json": ("application/json", "file"),
    "xml":  ("application/xml", "file"),
    "html": ("text/html", "file"),
    "htm":  ("text/html", "file"),
    "rtf":  ("application/rtf", "file"),
    "epub": ("application/epub+zip", "file"),
    "zip":  ("application/zip", "file"),
    "rar":  ("application/vnd.rar", "file"),
    "7z":   ("application/x-7z-compressed", "file"),
    "tar":  ("application/x-tar", "file"),
    "gz":   ("application/gzip", "file"),
}


def get_file_info(file_path: str):
    """返回 (ext, contentType, bizType)。不依赖系统 mimetypes。"""
    name = os.path.basename(file_path)
    idx = name.rfind(".")
    ext = name[idx + 1:].lower() if idx >= 0 else "bin"

    if ext in MIME_MAP:
        content_type, biz_type = MIME_MAP[ext]
        return ext, content_type, biz_type

    return (ext or "bin"), "application/octet-stream", "file"
    # return "png","image/png","image"

# ==================== token / lid ====================
def utf8_to_base64(s: str) -> str:
    return base64.b64encode(s.encode("utf-8")).decode("ascii")


def parse_ai_tab_frame_base_data(html: str):
    m = re.search(
        r'<script[^>]*name=["\']?aiTabFrameBaseData["\']?[^>]*>([\s\S]*?)</script>',
        html,
        re.IGNORECASE,
    )
    if not m:
        return None
    try:
        data = json.loads(m.group(1))
    except json.JSONDecodeError:
        return None
    if data.get("token") and data.get("lid"):
        return {"token": data["token"], "lid": data["lid"]}
    return None


def fetch_token_and_lid(force_refresh: bool = False):
    if not force_refresh:
        cached = load_cached_token()
        if cached:
            log("      [cache] 使用本地缓存 token/lid")
            return cached

    log("      [http] 请求 token/lid 页面")
    resp = SESSION.get(
        TOKEN_LID_URL,
        headers={
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
        timeout=20,
    )
    resp.raise_for_status()
    parsed = parse_ai_tab_frame_base_data(resp.text)
    if not parsed:
        raise RuntimeError("响应中未找到 aiTabFrameBaseData（可能未登录，或页面结构已变）")

    save_cached_token(parsed["token"], parsed["lid"])
    return parsed["token"], parsed["lid"]


def generate_chat_token(token: str, lid: str) -> str:
    """
    chat_token = base64(token|md5(query)|ts|lid) + "-" + lid + "-3"
    上传场景 query 为空，md5('') = d41d8cd98f00b204e9800998ecf8427e
    """
    md5_empty = hashlib.md5(b"").hexdigest()
    ts = str(int(time.time() * 1000))
    payload = f"{token}|{md5_empty}|{ts}|{lid}"
    b64 = utf8_to_base64(payload)
    return f"{b64}-{lid}-3"


# ==================== BOS V4 签名 ====================
RESERVED_CHARS = set(string.ascii_letters + string.digits + ".~-_")


def uri_encode(s: str, encode_slash: bool = True) -> str:
    result = []
    for ch in s:
        if ch in RESERVED_CHARS:
            result.append(ch)
        elif ch == "/" and not encode_slash:
            result.append(ch)
        else:
            result.append("%" + format(ord(ch), "02X"))
    return "".join(result)


def build_canonical_query(params):
    if not params:
        return ""
    items = params.items() if isinstance(params, dict) else params
    encoded = []
    for k, v in items:
        encoded.append((uri_encode(str(k)), uri_encode(str(v))))
    encoded.sort(key=lambda x: x[0])
    return "&".join(f"{k}={v}" for k, v in encoded)


def build_bos_auth(method, host, path, query_string, headers, ak, sk, bce_date, expire):
    norm = {}
    for k, v in headers.items():
        norm[k.lower()] = str(v).strip()
    norm["host"] = host

    header_keys = sorted(norm.keys())
    signed_headers = ";".join(header_keys)
    canonical_headers = "\n".join(
        f"{k}:{uri_encode(norm[k], encode_slash=True)}" for k in header_keys
    )

    auth_prefix = f"bce-auth-v1/{ak}/{bce_date}/{expire}"

    signing_key = hmac.new(
        sk.encode("utf-8"),
        auth_prefix.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    encoded_path = uri_encode(path, encode_slash=False)
    canonical_request = "\n".join(
        [method, encoded_path, query_string or "", canonical_headers]
    )

    signature = hmac.new(
        signing_key.encode("utf-8"),
        canonical_request.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    return f"{auth_prefix}/{signed_headers}/{signature}"


def now_bce_date() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ==================== STS ====================
def fetch_sts(chat_token: str) -> dict:
    url = f"{STS_URL}?tk={quote(chat_token, safe='')}&isPrivateChat={str(IS_PRIVATE_CHAT).lower()}"
    resp = SESSION.get(
        url,
        headers={
            "Accept": "*/*",
            "Origin": "https://wenxin.baidu.com",
            "Referer": "https://wenxin.baidu.com/",
        },
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    if data.get("status") != 0 or not data.get("data"):
        raise RuntimeError(f"STS 返回失败: {data.get('message') or data}")
    return data["data"]


# ==================== BOS 路径 ====================
def build_bos_path(sts: dict, object_key: str) -> str:
    prefix = sts.get("preFixPath", "")
    if prefix.startswith("/"):
        prefix = prefix[1:]
    if not prefix.endswith("/"):
        prefix += "/"
    return f"/{prefix}{object_key}"


# ==================== 上传（simple PUT） ====================
def upload_to_bos(sts: dict, file_bytes: bytes, object_key: str, content_type: str):
    path = build_bos_path(sts, object_key)
    url = f"https://{BASE_HOST}{path}"
    bce_date = now_bce_date()
    content_length = str(len(file_bytes))

    sign_headers = {
        "content-length": content_length,
        "content-type": content_type,
        "x-bce-date": bce_date,
        "x-bce-security-token": sts["token"],
    }
    auth = build_bos_auth(
        method="PUT",
        host=BASE_HOST,
        path=path,
        query_string="",
        headers=sign_headers,
        ak=sts["ak"],
        sk=sts["sk"],
        bce_date=bce_date,
        expire=EXPIRE_SEC,
    )

    resp = SESSION.put(
        url,
        data=file_bytes,
        headers={
            "Content-Type": content_type,
            "Content-Length": content_length,
            "x-bce-date": bce_date,
            "x-bce-security-token": sts["token"],
            "Authorization": auth,
        },
        timeout=120,
    )
    if not (200 <= resp.status_code < 300):
        raise RuntimeError(f"PUT {resp.status_code}: {resp.text[:300]}")


# ==================== 登记文件 ====================
def register_file(sts, chat_token, object_key, file_name, file_size,
                  content_type, biz_type):
    id_b64 = utf8_to_base64(object_key)

    prefix = sts.get("preFixPath", "").lstrip("/")
    path = (prefix + object_key).replace("//", "/")

    payload = {
        "path": path,
        "size": file_size,
        "name": file_name,
        "id": id_b64,
        "type": biz_type,
        "contentType": content_type,
    }

    resp = SESSION.post(
        f"{REGISTER_URL}?tk={quote(chat_token, safe='')}",
        headers={
            "Content-Type": "application/json",
            "Accept": "*/*",
            "Origin": "https://wenxin.baidu.com",
            "Referer": "https://wenxin.baidu.com/",
        },
        data=json.dumps(payload),
        timeout=30,
    )
    if not (200 <= resp.status_code < 300):
        raise RuntimeError(f"register HTTP {resp.status_code}: {resp.text[:300]}")

    data = resp.json()
    if data.get("status") not in (0, None):
        raise RuntimeError(f"register 业务失败: {data}")

    inner = data.get("data") or data.get("result") or data
    file_url = (
        inner.get("file_url")
        or inner.get("fileUrl")
        or inner.get("url")
        or (inner.get("file") or {}).get("file_url")
        or (inner.get("file") or {}).get("url")
    )
    if not file_url:
        raise RuntimeError(
            f"登记成功但未找到 file_url: {json.dumps(data, ensure_ascii=False)[:400]}"
        )
    return file_url


# ==================== 工具函数 ====================
def random_object_key(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1] or ".bin"
    rand = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"{int(time.time() * 1000)}-{rand}{ext}"


# ==================== 主流程 ====================
def upload_local_file(file_path: str) -> str:
    if not os.path.isfile(file_path):
        raise FileNotFoundError(file_path)

    with open(file_path, "rb") as f:
        file_bytes = f.read()

    file_name = os.path.basename(file_path)
    file_size = len(file_bytes)
    _, content_type, biz_type = get_file_info(file_path)
    object_key = random_object_key(file_path)

    log(f"[1/5] {file_name} ({file_size} bytes, {content_type}, type={biz_type})")

    # token / lid
    token, lid = fetch_token_and_lid()
    chat_token = generate_chat_token(token, lid)

    # STS（失败时清掉缓存 token 重试一次）
    try:
        sts = fetch_sts(chat_token)
    except Exception as e:
        log(f"      [retry] STS 失败：{e}，强制刷新 token/lid 后重试")
        clear_cached_token()
        token, lid = fetch_token_and_lid(force_refresh=True)
        chat_token = generate_chat_token(token, lid)
        sts = fetch_sts(chat_token)

    log(f"[2/5] STS ak={sts['ak'][:8]}... preFixPath={sts.get('preFixPath', '')}")

    # 上传 BOS
    upload_to_bos(sts, file_bytes, object_key, content_type)
    log("[3/5] BOS 上传成功")

    # 登记
    file_url = register_file(
        sts, chat_token, object_key, file_name, file_size,
        content_type, biz_type,
    )
    log(f"[4/5] file_url = {file_url}")
    return file_url


# ==================== main ====================
def main() -> int:
    args = [a for a in sys.argv[1:] if a]
    if not args:
        print("用法: python wenxin_upload.py <本地文件路径> [更多文件...]", file=sys.stderr)
        return 1

    failed = 0
    for path in args:
        try:
            url = upload_local_file(path)
        except Exception as e:
            failed += 1
            print(f"[ERROR] {path}: {e}", file=sys.stderr, flush=True)
            continue

        # ⚠️ Typora 只认 stdout 里的 URL 行；这里绝对不要加其他输出
        sys.stdout.write(url + "\n")
        sys.stdout.flush()

    return 0 if failed == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
