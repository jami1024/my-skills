# Wiki 数据约定

## 推荐目录

```text
<WIKI_ROOT>/
├── raw/<topic>/<slug>.md       # 来源材料或清洗稿
└── wiki/
    ├── <topic>/<slug>.md       # 知识条目
    ├── index.md                # 条目入口
    └── log.md                  # 入库与维护记录
```

`<topic>` 和 `<slug>` 使用小写英文、数字和连字符；已有仓库约定优先于本约定。

## raw 条目

```yaml
---
title: 原始标题
type: article
source_url: https://example.com/...
author: 未提供
published_at: 未提供
fetched_at: 2026-01-01
status: captured
---
```

正文应尽量保留来源原貌。清洗动作（去字幕噪声、合并断行、删除重复段落）写在文件末尾的 `Processing notes` 中。

## wiki 条目

```yaml
---
title: 条目标题
topic: ai-agents
source:
  - ../raw/ai-agents/example.md
status: draft
updated_at: 2026-01-01
---
```

推荐正文顺序：一句话摘要、核心判断、证据与引用、概念解释、关联条目、未解决问题、来源。

## 证据规则

- 原文没有给出的时间、数字、身份和结论写“未提供”。
- 引用必须保留原文，并附能复查的定位。
- 个人归纳使用“归纳”；跨资料推演使用“推演”；不要把二者伪装成原话。
- 转载内容应保留原始 URL 和作者信息，不能只留下二手摘要。
