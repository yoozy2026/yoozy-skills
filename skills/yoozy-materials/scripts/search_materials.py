#!/usr/bin/env python3
"""按关键词查询 Yoozy 在线物料库，单次请求一页视频或图文素材。"""

from __future__ import annotations

import argparse
import json
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen


# 复用已有公开列表接口，不依赖管理端地址、登录凭据或本地物料快照。
API_URL = "https://y.yoozyai.com/api/em/materials"


def search_materials(keyword: str, kind: str = "video", page: int = 1, size: int = 10) -> dict:
    """服务端完成关键词匹配与分页；客户端保留原始物料字段及媒体地址。"""
    keyword = keyword.strip()
    if not keyword:
        raise ValueError("搜索关键词不能为空")
    if kind not in ("video", "image") or page < 1 or not 1 <= size <= 100:
        raise ValueError("kind 必须为 video 或 image，page 至少为 1，size 为 1–100")
    query = urlencode({"keyword": keyword, "kind": kind, "page": page, "size": size})
    try:
        # 一次调用只发送一次 GET，不自动翻页或重试，避免批量遍历在线物料库。
        with urlopen(f"{API_URL}?{query}", timeout=30) as response:
            payload = json.load(response)
    except HTTPError as error:
        # 不回显网关错误页或完整远端响应，错误状态足够定位请求失败。
        raise ValueError(f"物料接口请求失败：HTTP {error.code}") from error
    except URLError as error:
        raise ValueError(f"物料接口连接失败：{error.reason}") from error
    if not isinstance(payload, dict) or payload.get("code") not in (None, "", 0, "0", "OK"):
        raise ValueError("物料接口返回业务错误")
    result = payload.get("data", payload)
    # 先确认分页协议，避免把错误信封当作空结果。服务端的 protobuf JSON 会省略
    # 空数组和零值；仅在有效分页响应中补回 list=[]、total=0，保持空匹配正常返回。
    if not isinstance(result, dict) or any(field not in result for field in ("page", "size")):
        raise ValueError("物料接口缺少分页信息")
    result.setdefault("list", [])
    result.setdefault("total", 0)
    if not isinstance(result["list"], list):
        raise ValueError("物料接口 list 不是数组")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--keyword", required=True, help="标签、提示词、脚本、摘要或媒体描述中的关键词")
    parser.add_argument("--kind", choices=("video", "image"), default="video")
    parser.add_argument("--page", type=int, default=1)
    parser.add_argument("--size", type=int, default=10)
    args = parser.parse_args()
    result = search_materials(args.keyword, args.kind, args.page, args.size)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as error:
        print(f"搜索失败：{error}", file=sys.stderr)
        sys.exit(1)
