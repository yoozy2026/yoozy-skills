#!/usr/bin/env python3
"""离线检查物料搜索技能的入口、UI 元数据、脚本与本地引用。"""

from __future__ import annotations

from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

import yaml


ROOT = Path(__file__).resolve().parents[1]


def check() -> None:
    skills = sorted((ROOT / "skills").glob("*/SKILL.md"))
    # 当前产品只发布一个搜索技能，避免旧创作技能残留后被安装器继续发现。
    if [path.parent.name for path in skills] != ["yoozy-materials"]:
        raise ValueError("当前只应包含 yoozy-materials 搜索技能")
    for path in skills:
        text = path.read_text(encoding="utf-8")
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
        if not (path.parent / "scripts/search_materials.py").is_file():
            raise ValueError("物料搜索脚本不存在")

    # 检查 Markdown 本地文件引用；技能引用只能落在自己的目录，保证单个安装包自包含。
    documents = [ROOT / "README.md", *(ROOT / "skills").rglob("*.md")]
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

    print("包检查通过：仅包含物料库搜索技能，入口和本地引用完整。")


if __name__ == "__main__":
    try:
        check()
    except (OSError, ValueError, KeyError, yaml.YAMLError) as error:
        print(f"包检查失败：{error}", file=sys.stderr)
        sys.exit(1)
