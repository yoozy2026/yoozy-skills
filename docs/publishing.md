# 发布完整经验

目前公开接口仅返回目录。完整正文需由有权访问的维护者从已有后台导出；本仓库不提供管理端登录、权限绕过或数据库抓取。

## 准备公开版本

1. 把后台导出放进 `private/`，避免原始导出被 Git 跟踪。
2. 只保留有权按本仓库许可证公开的条目。检查正文中的客户名称、素材链接、账号、内部路径、凭据及业务数据；需要改写时先完成改写。
3. 导出 JSON 支持数组、`{"list": [...]}` 或 `{"data": {"list": [...]}}`，与现有知识列表响应一致。每条使用 `_id`、`title`、`summary`、`content`、`category`、`tags`；只发布 `category=best_practice` 的完整正文。

审核后的正文保存在 `private/public-knowledge.json`。计算正文哈希：

```bash
python3 scripts/export_knowledge.py --input private/public-knowledge.json --hashes
```

这个命令只输出 ID 和 SHA-256，不输出正文。把选择发布的条目写入 `private/publication.json`：

```json
[
  {
    "id": "后台导出的真实经验ID",
    "slug": "yoozy-your-skill-name",
    "sha256": "审核后正文的完整SHA-256"
  }
]
```

清单代表维护者对这个正文版本的选择。脚本逐项验证 ID、分类、非空正文、技能名和哈希；任何一项不符都会在写文件前退出。哈希只确认版本一致，不能判断内容是否可公开。

## 生成与验证

```bash
python3 scripts/export_knowledge.py \
  --input private/public-knowledge.json \
  --manifest private/publication.json \
  --output skills

python3 scripts/check_package.py
git diff --stat
```

生成目录包含 `SKILL.md`、本地 UI 元数据和 `references/source.json`。标题、摘要作为入口元数据，正文按原样保留。内网工具名、外部依赖、相对附件链接不会自动转换，发布前必须检查可执行性；需要外部工具的经验应说明所需能力与失败时的交付方式。检查器会拒绝缺失的本地文件链接。

脚本拒绝覆盖现有目录。更新已发布经验时，先在 `private/staging/` 生成新版本，比较并替换已审核的文件，避免误覆盖手工维护的技能。

不要把 `private/` 中的原始导出或清单提交到公共仓库。提交前阅读 `git diff --cached`；目录快照、来源记录与示例均须与实际发布内容一致。
