# 知识库结构定义 (Schema)

## 数据库概览

```
lifedatabase/
├── sources/     # 原始数据 (Raw)
├── memory/      # 编译知识 (Compiled)
├── outputs/     # 产出物 (Artifacts)
├── templates/   # 模板 (Templates)
└── .gbrain/     # 配置 (Config)
```

## memory/ 结构定义

### concepts/ 概念库
```yaml
结构:
  - name: 概念名称
  - definition: 定义
  - related: [关联概念列表]
  - tags: [标签]
  - source: 来源
```

### people/ 人物库
```yaml
结构:
  - name: 姓名
  - role: 角色/身份
  - contact: 联系方式
  - tags: [标签]
  - timeline: [时间线]
  - notes: 备注
```

### projects/ 项目库
```yaml
结构:
  - name: 项目名称
  - status: 状态 (active/paused/completed)
  - start_date: 开始日期
  - goals: [目标]
  - progress: 进度
  - timeline: [时间线]
```

### decisions/ 决策库
```yaml
结构:
  - decision: 决策内容
  - date: 日期
  - context: 背景
  - alternatives: [备选方案]
  - outcome: 结果
  - lessons: 教训
```

### insights/ 洞察库
```yaml
结构:
  - insight: 洞察内容
  - category: 分类
  - source: 来源
  - date: 日期
  - impact: 影响程度
```

### accounts/ 账号库 (GBrain式)
```yaml
结构:
  - platform: 平台名称
  - username: 用户名
  - state: 当前状态
  - metrics: 指标数据
  - timeline: 时间线事件
  - assessment: 评估
  - open_threads: 待处理事项
```

## sources/ 结构定义

### social/ 社交媒体
```yaml
结构:
  - platform: 平台
  - content_type: 内容类型 (视频/图文/文章)
  - date: 发布/采集日期
  - url: 原始链接
  - content: 内容摘要
  - engagement: 互动数据
  - notes: 备注
```

## outputs/ 结构定义

### reports/ 报告
```yaml
结构:
  - title: 标题
  - type: 报告类型
  - date: 生成日期
  - sources: [参考来源]
  - content: 内容
```

### plans/ 计划
```yaml
结构:
  - title: 标题
  - type: 计划类型
  - start_date: 开始日期
  - end_date: 结束日期
  - milestones: [里程碑]
  - status: 状态
```

## .gbrain/ 配置结构

```json
{
  "version": "1.0",
  "sync": {
    "github_repo": "lifedatabase",
    "branch": "main",
    "auto_sync": true,
    "sync_interval": "daily"
  },
  "dream_config": {
    "enabled": true,
    "schedule": "02:00",
    "tasks": [
      "scan_conversations",
      "extract_knowledge",
      "update_index",
      "generate_report"
    ]
  },
  "search": {
    "engine": "sqlite_fts5",
    "db_path": ".gbrain/gbrain.db"
  }
}
```

## 页面模板变量

| 变量 | 说明 |
|------|------|
| {{title}} | 页面标题 |
| {{date}} | 创建/更新日期 |
| {{tags}} | 标签列表 |
| {{related}} | 关联页面 |
| {{source}} | 来源 |
