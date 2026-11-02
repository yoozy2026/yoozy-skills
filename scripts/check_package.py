#!/usr/bin/env python3
"""离线检查技能分发结构、引用、目录字段与导出正文的版本一致性。"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

import yaml


ROOT = Path(__file__).resolve().parents[1]


def check() -> None:
    skills = sorted((ROOT / "skills").glob("*/SKILL.md"))
    if not skills:
        raise ValueError("没有可安装技能")
    for path in skills:
        # 以原始字节解码，避免通用换行转换改变导入正文的 CRLF，导致来源哈希误报。
        text = path.read_bytes().decode("utf-8")
        if not text.startswith("---\n") or "\n---\n" not in text[4:]:
            raise ValueError(f"缺少 YAML frontmatter：{path}")
        header, body = text[4:].split("\n---\n", 1)
        metadata = yaml.safe_load(header)
        name = path.parent.name
        if not re.fullmatch(r"yoozy-[a-z0-9]+(?:-[a-z0-9]+)*", name) or len(name) > 64:
            raise ValueError(f"技能目录名无效：{name}")
        if not isinstance(metadata, dict) or metadata.get("name") != name:
            raise ValueError(f"技能名与目录不匹配：{name}")
        description = metadata.get("description")
        if not isinstance(description, str) or not description.strip() or len(description) > 1024:
            raise ValueError(f"技能 description 无效：{name}")
        if not body.strip() or re.search(r"\[TODO[^\]]*\]", body):
            raise ValueError(f"技能正文为空或仍有脚手架占位：{name}")
        ui = yaml.safe_load((path.parent / "agents/openai.yaml").read_text(encoding="utf-8"))
        if not isinstance(ui, dict) or not isinstance(ui.get("interface"), dict):
            raise ValueError(f"UI 元数据无效：{name}")
        if f"${name}" not in ui["interface"].get("default_prompt", ""):
            raise ValueError(f"默认提示缺少技能引用：{name}")
        source = path.parent / "references/source.json"
        if source.exists():
            # 导出器在结束 frontmatter 后额外加一个换行；移除这一固定分隔符后校验原文。
            provenance = json.loads(source.read_text(encoding="utf-8"))
            if not body.startswith("\n") or hashlib.sha256(body[1:].encode("utf-8")).hexdigest() != provenance["content_sha256"]:
                raise ValueError(f"导入正文与来源哈希不一致：{name}")

    # 检查 Markdown 本地文件引用；技能引用只能落在自己的目录，保证单个安装包自包含。
    documents = [ROOT / "README.md", *(ROOT / "docs").glob("*.md"), *(ROOT / "examples").glob("*.md"), *(ROOT / "skills").rglob("*.md")]
    for path in documents:
        text = re.sub(r"```.*?```", "", path.read_text(encoding="utf-8"), flags=re.S)
        for target in re.findall(r"\[[^\]]*\]\(([^\s)]+)\)", text):
            parsed = urlsplit(target.strip("<>"))
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            resolved = (path.parent / unquote(parsed.path)).resolve()
            if not resolved.exists():
                raise ValueError(f"本地引用不存在：{path.relative_to(ROOT)} -> {target}")
            if path.is_relative_to(ROOT / "skills"):
                skill_root = ROOT / "skills" / path.relative_to(ROOT / "skills").parts[0]
                if not resolved.is_relative_to(skill_root):
                    raise ValueError(f"技能引用依赖安装包外文件：{path} -> {target}")

    snapshot = json.loads((ROOT / "skills/yoozy-materials/references/catalog.json").read_text(encoding="utf-8"))
    seen = set()
    for item in snapshot["items"]:
        if set(item) != {"_id", "title", "summary"}:
            raise ValueError("公开目录出现字段白名单以外的内容")
        if any(not isinstance(value, str) for value in item.values()) or not item["title"].strip():
            raise ValueError("公开目录字段类型或标题无效")
        if not re.fullmatch(r"[a-fA-F0-9]{24}", item["_id"]) or item["_id"] in seen:
            raise ValueError("公开目录存在无效或重复 ID")
        seen.add(item["_id"])
    print(f"包检查通过：{len(skills)} 个独立技能，{len(seen)} 条公开目录记录，本地引用完整。")


if __name__ == "__main__":
    try:
        check()
    except (OSError, ValueError, KeyError, yaml.YAMLError) as error:
        print(f"包检查失败：{error}", file=sys.stderr)
        sys.exit(1)
