# lifedatabase 工作指南

## 核心原则
本知识库遵循 **三层架构**：sources → memory → outputs

## 目录职责

### sources/ (原始输入层 - 只追加，不修改)
- `articles/` - 文章/博客存档
- `videos/` - 视频笔记
- `podcasts/` - 播客内容
- `pdfs/` - PDF文档
- `ppts/` - PPT幻灯片
- `social/` - 社交媒体数据
  - `douyin/` - 抖音数据
  - `bilibili/` - B站数据
  - `xiaohongshu/` - 小红书数据

### memory/ (知识层 - 编译后知识，可重写)
- `context/` - 背景/上下文信息
- `accounts/` - 账号/平台数据（GBrain式Timeline）
- `projects/` - 项目记录
- `scripts/` - 脚本代码
- `concepts/` - 概念定义
- `people/` - 人物信息
- `decisions/` - 决策记录
- `insights/` - 洞察总结
- `index.md` - 知识索引
- `recent.md` - 最近更新

### outputs/ (产出物层)
- `ppts/` - 生成的PPT
- `reports/` - 报告文档
- `plans/` - 计划方案

## 页面结构 (GBrain格式)

每个页面采用以下结构：
```markdown
# 标题

## State (当前状态)
- 描述当前状态

## Assessment (评估)
- 分析和判断

## Open Threads (待处理)
- [ ] 待办事项1
- [ ] 待办事项2

## Timeline (时间线)
- 日期: 事件描述
```

## 工作流程

### 添加新内容
1. 将原始素材放入 `sources/` 对应目录
2. 在 `memory/` 创建或更新相关页面
3. 更新 `index.md` 和 `recent.md`

### 知识编译
1. 从 sources 提取关键信息
2. 归类到 memory 的适当目录
3. 保持概念和洞察的关联性

### 产出生成
1. 从 memory 提取相关知识
2. 生成 outputs/ 下的产出物
3. 标注来源以便追溯

## Git同步策略
- 每日自动同步（梦境循环）
- 重要变更后手动同步
- 保持本地与云端一致

## 命名规范
- 文件名：中文可用，英文推荐下划线
- 链接：使用相对路径
- 图片：放入同目录或指定assets文件夹
