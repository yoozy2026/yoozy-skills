# 来源与内容状态

## Yoozy 公开经验目录

来源：<https://y.yoozyai.com/api/em/knowledges?page=1&size=100>。

仓库快照保存于 `skills/yoozy-materials/references/catalog.json`，采集时间以文件中的 `fetched_at` 为准。接口只提供 `_id`、`title` 和 `summary`；本项目只保留这些字段。条目数量、标题和摘要可能随后变化。

技能依据以下公开摘要整理；技能内的镜头表、事实清单和交付格式属于本项目新增的执行约定，不代表读取过完整正文：

| 技能 | 目录条目 | 经验 ID |
| --- | --- | --- |
| `yoozy-product-video` | 一键生成高光带货视频 | `6ae85456544b40c1d3a1c821` |
| `yoozy-talking-head` | 真人口播短视频带货 | `6ae81ff0544b40c1d3a1c820` |
| `yoozy-drama-video` | 短剧带货视频生成经验 | `6ae411c59ea282418d10d8f0` |

健康素材、视频复刻、母婴素材和旧版一键带货条目目前仅提供目录发现。目录没有暴露正文，不据此编造详细指令；需要相应工作时，应说明当前公开范围，并依据用户提供的信息处理。

## 项目形式参考

- [taishang-laojun](https://github.com/liuhaisi2026212-maker/taishang-laojun)：参考了“技能目录 + 人读说明 + 示例 + 包检查”的分发形式。未复制其文字、方法、案例、图示或品牌内容。
- [Skills CLI](https://github.com/vercel-labs/skills)：用于发现和安装技能；它是外部安装工具，不是本项目的运行时依赖。
- [Agent Skills specification](https://agentskills.io/specification)：技能入口采用 `SKILL.md` 与 YAML frontmatter。

## 尚未包含

受保护的最佳实践正文、线上向量检索、Yoozy 私有模板、原始视频、客户数据和视频生成服务均不包含在本仓库中。公开目录刷新不会获取它们。

示例均为明确标注的虚构输入，没有实测的播放、成交或转化数据。新增真实经验应在对应技能的 `references/source.json` 中记录来源 ID 和正文哈希。
