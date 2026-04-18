# 知识库Schema定义

> 本文档定义知识库的数据结构规范。所有新增页面需遵循此规范。

---

## 一、页面类型

| 类型 | 目录 | 说明 | Frontmatter字段 |
|------|------|------|----------------|
| account | memory/accounts/ | 社媒账号档案 | type, platform, followers |
| project | memory/projects/ | 项目档案 | type, status, start_date |
| person | memory/people/ | 人物档案 | type, role, organization |
| concept | memory/concepts/ | 概念解释 | type, category, related |
| decision | memory/decisions/ | 决策记录 | type, date, status |
| insight | memory/insights/ | 洞察总结 | type, source, date |
| script | memory/scripts/ | 定稿脚本 | type, platform, publish_date |
| context | memory/context/ | 背景知识 | type, topic, last_updated |

---

## 二、通用页面结构

所有memory页面采用 **Compiled Truth + Timeline** 结构：

```markdown
---
title: 页面标题
type: account/project/person...
tags: [tag1, tag2]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# 页面标题

## State（当前状态）
最新信息的汇总，随时可被重写

## Assessment（判断）
分析和评估结论

## Open Threads（开放问题）
- [ ] 待跟进事项1
- [ ] 待跟进事项2

---

## Timeline（时间线）

**YYYY-MM-DD** | 事件类型 — 事件描述
```

---

## 三、Frontmatter规范

### 账号档案（account）
```yaml
---
title: 账号名称
type: account
platform: douyin/bilibili/xiaohongshu/youtube
followers: 粉丝数
tags: [领域标签]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

### 项目档案（project）
```yaml
---
title: 项目名称
type: project
status: planning/active/completed
start_date: YYYY-MM-DD
end_date: YYYY-MM-DD
tags: [标签]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

---

## 四、命名规范

- 文件名使用中文，与页面标题一致
- 避免特殊字符和空格
- 保持简洁明了

示例：
- `memory/accounts/钟钟的AI圈.md`
- `memory/projects/知识库搭建.md`

---

## 五、标签规范

### 平台标签
- `#平台/抖音`
- `#平台/B站`
- `#平台/小红书`
- `#平台/YouTube`

### 内容标签
- `#内容/知识付费`
- `#内容/AI`
- `#内容/个人成长`
- `#内容/职场`

### 状态标签
- `#状态/进行中`
- `#状态/已完成`
- `#状态/观察中`

---

*最后更新：2026-04-18*
