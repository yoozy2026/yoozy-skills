#!/usr/bin/env python3
"""查询离线经验目录；显式 refresh 时只读取一次 Yoozy 公开元数据接口。"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys
from urllib.request import urlopen


# 路径相对技能本身解析，安装到任意宿主后仍能找到快照；不依赖项目根目录。
SNAPSHOT = Path(__file__).resolve().parents[1] / "references" / "catalog.json"
PUBLIC_URL = "https://y.yoozyai.com/api/em/knowledges?page=1&size=100"


def validate_items(items: object) -> list[dict]:
    """字段白名单确保服务端日后增加字段时，正文或其它数据不会自动进入分发包。"""
    if not isinstance(items, list):
        raise ValueError("目录响应缺少 list 数组")
    result, seen = [], set()
    for item in items:
        if not isinstance(item, dict):
            raise ValueError("目录条目必须为对象")
        selected = {key: item.get(key) for key in ("_id", "title", "summary")}
        if any(not isinstance(value, str) for value in selected.values()):
            raise ValueError("目录 ID、标题和摘要必须为字符串")
        if not re.fullmatch(r"[a-fA-F0-9]{24}", selected["_id"]) or not selected["title"].strip():
            raise ValueError("目录 ID 或标题无效")
        if selected["_id"] in seen:
            raise ValueError("目录中存在重复 ID")
        seen.add(selected["_id"])
        result.append(selected)
    return result


def refresh() -> dict:
    """完整验证后原子替换快照；网络、业务错误或分页截断均保留旧文件。"""
    with urlopen(PUBLIC_URL, timeout=30) as response:
        payload = json.load(response)
    if not isinstance(payload, dict) or payload.get("code") not in (None, 0, "0", "OK", ""):
        raise ValueError("公开接口返回业务错误")
    data = payload.get("data", payload)
    if not isinstance(data, dict):
        raise ValueError("公开接口 data 必须为对象")
    items = validate_items(data.get("list"))
    # 当前公开接口上限为 100。超出时拒绝写入部分目录，不在循环里请求后续页面。
    if data.get("total") != len(items):
        raise ValueError("公开目录未完整返回，快照未更新；请维护批量读取协议")
    snapshot = {
        "source": PUBLIC_URL,
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "items": items,
    }
    temporary = SNAPSHOT.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(SNAPSHOT)
    return snapshot


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list", help="读取全部离线目录")
    search = commands.add_parser("search", help="在离线标题、摘要和 ID 中做文本匹配")
    search.add_argument("keyword")
    commands.add_parser("refresh", help="一次请求刷新公开目录，不获取正文")
    args = parser.parse_args()
    snapshot = refresh() if args.command == "refresh" else json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    items = validate_items(snapshot["items"])
    if args.command == "search":
        keyword = args.keyword.strip().casefold()
        if not keyword:
            parser.error("搜索关键词不能为空")
        items = [item for item in items if keyword in " ".join(item.values()).casefold()]
    print(json.dumps({**snapshot, "items": items, "count": len(items)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError) as error:
        # 不回显远端响应正文，以免异常响应中出现不应进入日志的信息。
        print(f"目录操作失败：{error}", file=sys.stderr)
        sys.exit(1)
