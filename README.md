# Yoozy Skills · 物料库搜索

让智能体按关键词搜索 Yoozy 在线物料库，返回真实的视频、图文素材及其摘要、脚本、提示词和媒体链接。

## 安装

```bash
npx skills add yoozy2026/yoozy-skills --skill yoozy-materials
```

安装后直接对智能体说：

> 用 Yoozy 搜一下口播带货的视频物料。

> 找一下收纳类图文素材。

> 继续看下一页。

## 命令行

需要 Python 3.9 或以上，仅使用标准库，无需安装运行依赖或配置密钥。

```bash
python3 skills/yoozy-materials/scripts/search_materials.py --keyword '口播'
python3 skills/yoozy-materials/scripts/search_materials.py --keyword '收纳' --kind image
python3 skills/yoozy-materials/scripts/search_materials.py --keyword '口播' --page 2 --size 10
```

| 参数 | 说明 |
| --- | --- |
| `--keyword` | 必填，关键词，匹配标签、提示词、脚本、摘要和媒体描述 |
| `--kind` | `video`（默认）或 `image` |
| `--page` | 从 1 开始，默认 1 |
| `--size` | 每页 1–100 条，默认 10 |

复用现有开放搜索接口 `OpenService.SearchEcommerceMaterial`：`GET https://y.yoozyai.com/api/adm/ecommerce-knowledge-search-6f4a9c2e7b1d8a53`，返回 `MaterialList`。这是关键词模糊匹配，不是语义搜索；没有结果时可缩短关键词。每次只查询指定的一页，不自动遍历全库。

成功时输出服务端的 `list`、`total`、`page`、`size`。物料包含 `_id`、`extra.title`、`media`、`kind`、`tags`、`summary`、`script`、`prompt`、`keyFrames` 字段，具体以实际响应为准。失败时向 stderr 输出错误并返回非零退出码，不将失败当作空结果。

本项目目前只提供物料搜索。媒体链接来自接口，不代表授予素材的使用或转载许可。

## 维护

```bash
python3 -m pip install -r requirements-dev.txt
python3 scripts/check_package.py
```

采用 [MIT License](LICENSE)。
