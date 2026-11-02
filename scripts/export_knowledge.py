#!/usr/bin/env python3
"""将已审核的本地 best_practice 正文转换为独立可安装技能，不访问网络。"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys


def load_items(path: Path) -> dict[str, dict]:
    """兼容后台列表信封；先索引全部记录，拒绝重复 ID，避免审核对象被后项覆盖。"""
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        if data.get("code") not in (None, "", 0, "0", "OK"):
            raise ValueError("输入是业务错误响应，不能作为知识导出")
        data = data.get("data", data)
        if not isinstance(data, dict):
            raise ValueError("导出 data 必须为对象")
        data = data.get("list")
    if not isinstance(data, list):
        raise ValueError("输入应为数组或包含 list 的知识列表响应")
    items = {}
    for item in data:
        if not isinstance(item, dict) or not isinstance(item.get("_id"), str):
            raise ValueError("每条知识必须有字符串 _id")
        identity = item["_id"]
        if identity in items:
            raise ValueError(f"导出存在重复 ID：{identity}")
        items[identity] = item
    return items


def digest(content: str) -> str:
    """对原始 UTF-8 正文计算哈希；不裁剪空格或换行，确保审核版本精确匹配。"""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def prepare(items: dict[str, dict], manifest: object, output: Path) -> list[tuple[Path, dict[str, str]]]:
    """在任何写入前验证整个清单，仅将明确选中的条目加入发布计划。"""
    if not isinstance(manifest, list) or not manifest:
        raise ValueError("发布清单必须为非空数组")
    plan, seen_ids, seen_slugs = [], set(), set()
    for entry in manifest:
        if not isinstance(entry, dict):
            raise ValueError("发布清单条目必须为对象")
        identity, slug, reviewed_hash = (entry.get(key) for key in ("id", "slug", "sha256"))
        if not isinstance(identity, str) or not re.fullmatch(r"[a-fA-F0-9]{24}", identity):
            raise ValueError("发布 ID 必须为 24 位十六进制字符串")
        # slug 同时用作目录名，固定命名规则阻止路径穿越，也符合技能分发约定。
        if not isinstance(slug, str) or not re.fullmatch(r"yoozy-[a-z0-9]+(?:-[a-z0-9]+)*", slug) or len(slug) > 64:
            raise ValueError("slug 必须为不超过 64 字符的 yoozy- 小写连字符名称")
        if identity in seen_ids or slug in seen_slugs:
            raise ValueError("发布清单存在重复 ID 或技能名")
        seen_ids.add(identity)
        seen_slugs.add(slug)
        if identity not in items:
            raise ValueError(f"导出中找不到清单 ID：{identity}")
        item = items[identity]
        if item.get("category") != "best_practice":
            raise ValueError(f"条目不是 best_practice：{identity}")
        for field in ("title", "summary", "content"):
            if not isinstance(item.get(field), str) or not item[field].strip():
                raise ValueError(f"发布条目缺少 {field}：{identity}")
        if len(item["summary"]) > 1024:
            raise ValueError(f"摘要超过技能描述长度限制：{identity}")
        if reviewed_hash != digest(item["content"]):
            raise ValueError(f"正文与审核哈希不一致：{identity}")
        destination = output / slug
        if destination.exists() or destination.is_symlink():
            raise ValueError(f"拒绝覆盖现有目录：{destination}")

        # JSON 字符串也是合法 YAML 标量，避免标题或摘要里的冒号、换行改变 frontmatter。
        quote = lambda value: json.dumps(value, ensure_ascii=False)
        frontmatter = f"---\nname: {slug}\ndescription: {quote(item['summary'])}\n---\n\n"
        source = {"id": identity, "title": item["title"], "content_sha256": reviewed_hash}
        interface = {
            "display_name": item["title"],
            "short_description": item["summary"][:64],
            "default_prompt": f"用 ${slug} 帮我完成这次物料创作。",
        }
        # 正文直接拼接，不增加标题、不去空白，保留原 Markdown 的布局与语义。
        plan.append((destination, {
            "SKILL.md": frontmatter + item["content"],
            "references/source.json": json.dumps(source, ensure_ascii=False, indent=2) + "\n",
            "agents/openai.yaml": "interface:\n" + "".join(f"  {key}: {quote(value)}\n" for key, value in interface.items()),
        }))
    return plan


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1] / "skills")
    parser.add_argument("--hashes", action="store_true", help="只列出正文哈希，不输出正文或写文件")
    args = parser.parse_args()
    items = load_items(args.input)
    if args.hashes:
        hashes = [{"id": identity, "sha256": digest(item["content"])}
                  for identity, item in items.items() if isinstance(item.get("content"), str) and item["content"].strip()]
        print(json.dumps(hashes, ensure_ascii=False, indent=2))
        return
    if args.manifest is None:
        parser.error("发布必须提供 --manifest；只计算哈希请用 --hashes")
    plan = prepare(items, json.loads(args.manifest.read_text(encoding="utf-8")), args.output)
    for destination, files in plan:
        # mkdir 不允许覆盖；全部内容校验已结束，写入发生在显式选择的输出目录。
        destination.mkdir(parents=True, exist_ok=False)
        for relative, content in files.items():
            path = destination / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    print(json.dumps({"created": [str(path) for path, _ in plan]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as error:
        print(f"经验发布失败：{error}", file=sys.stderr)
        sys.exit(1)
