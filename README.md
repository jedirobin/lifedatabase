# lifedatabase 知识库

融合 Karpathy 三层架构 + GBrain 页面结构 的个人知识管理系统

## 🏗️ 架构概览

```
sources/     →  memory/      →  outputs/
(原始输入)     (编译知识)      (产出物)
    ↓             ↓             ↓
  只追加       可重写         归档
```

## 📁 目录结构

```
lifedatabase/
├── CLAUDE.md              # AI工作指南
├── TASKS.md               # 待办事项
├── sources/               # 原始数据层
│   ├── articles/          # 文章存档
│   ├── videos/            # 视频笔记
│   ├── podcasts/          # 播客内容
│   ├── pdfs/              # PDF文档
│   ├── ppts/              # PPT幻灯片
│   └── social/            # 社交媒体数据
│       ├── douyin/        # 抖音
│       ├── bilibili/      # B站
│       └── xiaohongshu/   # 小红书
├── memory/                # 知识层
│   ├── concepts/         # 概念库
│   ├── people/           # 人物库
│   ├── projects/         # 项目库
│   ├── decisions/        # 决策库
│   ├── insights/         # 洞察库
│   ├── accounts/         # 账号库
│   ├── index.md          # 知识索引
│   └── recent.md         # 最近更新
├── outputs/               # 产出层
│   ├── ppts/             # 生成PPT
│   ├── reports/          # 报告文档
│   └── plans/            # 计划方案
├── templates/             # 模板库
│   ├── account-template.md
│   ├── person-template.md
│   └── project-template.md
└── .gbrain/               # 配置目录
    ├── config.json       # 配置文件
    ├── gbrain.db         # SQLite数据库
    └── dream_loop.sh     # 梦境循环脚本
```

## 🚀 快速开始

### 1. 初始化Git仓库

```bash
cd lifedatabase
git init
git add .
git commit -m "Initial commit"
```

### 2. 推送到GitHub

在GitHub创建 `lifedatabase` 仓库后：

```bash
git remote add origin git@github.com:你的用户名/lifedatabase.git
git branch -M main
git push -u origin main
```

### 3. 配置梦境循环

```bash
# 添加定时任务
crontab -e
# 添加行: 0 2 * * * /root/lifedatabase/.gbrain/dream_loop.sh
```

## 📖 页面结构 (GBrain格式)

每个页面采用：

```markdown
## State (当前状态)
描述当前状态

## Assessment (评估)
分析和判断

## Open Threads (待处理)
- [ ] 待办事项

## Timeline (时间线)
- 日期: 事件
```

## 🔄 同步机制

| 触发 | 方式 |
|------|------|
| 手动 | `git push` / `git pull` |
| 自动 | 梦境循环（每日凌晨2点） |
| 移动端 | Obsidian Git插件 |

## 📚 相关文档

- [CLAUDE.md](./CLAUDE.md) - AI工作指南
- [知识库结构](./memory/schema.md) - Schema定义
- [数据采集方案](./docs/data-collection-plan.md) - 采集技术选型

## ✅ 待完成事项

- [ ] 配置GitHub仓库并完成首次同步
- [ ] 设置每日梦境循环日程
- [ ] 测试数据采集脚本

---

*lifedatabase - 让知识流动起来*
