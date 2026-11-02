# Yoozy Skills · 物料经验库

把商品图、人物图和创作需求，整理成能拍、能改、能交给视频生成工具执行的方案。

这里开放 Yoozy 的物料创作流程与经验目录，供支持 Agent Skills 的智能体使用。当前版本是 **0.1.0**：提供 4 个可安装技能、线上公开经验目录，以及完整经验正文的离线发布工具。

**内容状态：** 当前目录收录 Yoozy 公开接口返回的 7 条经验标题和摘要。三个视频技能依据其中的公开摘要独立整理，包含本项目新增的交付约定；它们不是受保护正文的原文导出，也没有线上投放效果验证。完整经验正文尚未导入，商业素材、客户资料和管理接口凭据不随仓库发布。

## 安装

需要 Node.js，版本要求以 [Skills CLI 官方说明](https://github.com/vercel-labs/skills#install-a-skill)为准。

```bash
npx skills add yoozy2026/yoozy-skills
```

按提示选择技能和目标智能体。也可以只安装一个：

```bash
npx skills add yoozy2026/yoozy-skills --skill yoozy-product-video
```

手动安装时，将 `skills/` 下需要的**整个技能文件夹**复制到宿主的技能目录，保留 `references/`、`scripts/` 和 `agents/`。安装与读取技能不需要 Yoozy 账号；实际生成视频需要宿主另外提供模型或工具。

## 直接这样用

| 想做什么 | 对智能体说 | 技能 |
| --- | --- | --- |
| 找适合的物料经验 | “用 Yoozy，只有商品图，适合做哪种带货视频？” | `yoozy-materials` |
| 做商品展示、只出手部或手机 POV | “用 Yoozy 商品高光视频，给这款收纳盒做一条 15 秒视频。” | `yoozy-product-video` |
| 用人物图和商品图做口播 | “用 Yoozy 真人口播，按这两张图写策略和完整分镜。” | `yoozy-talking-head` |
| 把商品自然放进剧情 | “用 Yoozy 短剧带货，设计一条 20 秒的办公室小短剧。” | `yoozy-drama-video` |

只问选型就给选型，只改一镜就改一镜。完整创作先给策略与分镜，确认方案后才使用可用的视频生成能力。没有生成工具时交付分镜和提示词，不报告已经出片。

[看一份完整的演示交付](examples/product-video.md) · [浏览经验目录](skills/yoozy-materials/references/catalog.json) · [查看来源与当前边界](docs/sources.md)

## 经验怎样开放

公开目录和完整技能分别维护：

- 公开目录：只同步标题、摘要和经验 ID。默认离线读取仓库快照；手动刷新时调用现有公开接口。
- 完整技能：维护者取得有权开放的 Markdown 正文，审核后通过明确的 ID、技能名和正文哈希导入。发布工具不会登录后台或导出数据库。

```bash
# 无网络也能查目录；关键词同时匹配标题、摘要和 ID。
python3 skills/yoozy-materials/scripts/catalog.py search '口播'

# 一次请求刷新公开目录；失败时保留原快照。
python3 skills/yoozy-materials/scripts/catalog.py refresh

# 用仓库内标注为演示的数据验证完整正文发布，不写入正式技能目录。
python3 scripts/export_knowledge.py \
  --input examples/knowledge-export.demo.json \
  --manifest examples/publication.demo.json \
  --output /tmp/yoozy-skills-demo
```

真实经验的发布方式见[经验发布说明](docs/publishing.md)。把目录装进智能体，不等于取得目录背后的受保护正文或视频文件。

## 维护与贡献

欢迎提交可复用的创作经验、失败边界和有来源的复盘。经验应说明适用条件、执行步骤、产物与不适用情况；演示和实测分开标注，不用编造的播放量、转化率或客户案例支撑结论。

修改后执行：

```bash
python3 -m pip install -r requirements-dev.txt
python3 scripts/check_package.py
```

本项目采用 [MIT License](LICENSE)。参考项目仅用于了解技能项目的组织与分发形式，没有复制其技能正文、案例或品牌表达。来源说明见 [docs/sources.md](docs/sources.md)。
