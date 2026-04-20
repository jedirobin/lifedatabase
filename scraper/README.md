# 🚀 GrabLab - 智能多平台爬虫 + 知识库系统

基于 Karpathy 三层架构的智能爬虫系统，自动抓取、分析并同步到 Obsidian 知识库。

## ✨ 核心功能

### 📱 社媒爬虫
- **B站** - 热门视频、UP主作品数据抓取
- **抖音** - 热门视频、达人数据分析
- **小红书** - 热门笔记、爆款内容拆解
- **自动生成爆款创作SKILL** - NLP关键词提取+规律分析

### 🛒 电商选品
- **闲鱼/1688/拼多多** 销量榜单抓取
- **自动利润计算** - 服务费+运费+成本自动核算
- **选品评级** - S/A/B/C四级智能推荐
- **生成选品分析报告**

### 📦 知识库同步
- 数据自动归档到 `sources/` 目录
- 分析报告同步到 `outputs/reports/`
- 爆款SKILL写入 `memory/insights/`
- **Git自动备份** - 完成后自动提交推送

### ⏰ 定时任务
- 每日自动执行爬虫任务
- 支持自定义调度时间
- 多任务顺序执行避免冲突

---

## 🚀 快速开始

### 1. 安装依赖
```bash
cd scraper
pip install -r requirements.txt
```

### 2. 单次运行（推荐首次测试）
```bash
# 运行全部平台爬虫+分析
python main.py --once

# 只运行B站
python main.py -p bilibili

# 指定抓取数量
python main.py -p xiaohongshu -l 100
```

### 3. 启动定时调度
```bash
python main.py --scheduler
```

---

## 📁 项目结构

```
scraper/
├── main.py                    # 主入口
├── config.py                  # 全局配置
├── requirements.txt           # 依赖
├── README.md                  # 本文档
│
├── base_scraper.py            # 爬虫基类（统一框架）
├── obsidian_sync.py           # Obsidian同步模块
│
├── platforms/                 # 各平台爬虫
│   ├── bilibili.py            # B站爬虫
│   ├── douyin.py              # 抖音爬虫
│   └── xiaohongshu.py         # 小红书爬虫
│
├── analyzers/
│   ├── content_analyzer.py    # 爆款内容NLP分析
│   └── product_analyzer.py    # 电商选品+利润计算
│
├── scheduler/
│   └── task_scheduler.py      # 定时任务调度
│
└── data/                      # 原始数据存档
```

---

## 🎯 使用示例

### 利润计算公式
```
净利润 = 售价 - 进货价 - 运费(¥8) - 平台服务费(6%)

推荐标准：净利润≥¥20 且 利润率≥25%
```

### 评级标准
| 评级 | 利润要求 | 利润率要求 |
|------|----------|------------|
| S级 | ¥50+ | 50%+ |
| A级 | ¥30+ | 35%+ |
| B级 | ¥20+ | 25%+ |
| C级 | ¥10+ | - |

---

## 🔧 配置说明

编辑 `config.py` 自定义：

```python
PROFIT_CONFIG = {
    "platform_fee_rate": 0.06,      # 平台服务费
    "shipping_cost": 8,             # 运费
    "min_profit_margin": 20,        # 最低利润
    "target_profit_rate": 0.3       # 目标利润率
}
```

---

## 📊 输出示例

运行完成后，会自动在Obsidian生成：

1. **`memory/insights/[平台]爆款创作SKILL.md`**
   - 爆款标题关键词TOP30
   - 标题公式成功概率分析
   - 可落地的创作建议

2. **`memory/insights/电商选品SKILL.md`**
   - Top15推荐商品清单
   - 分品类利润对比
   - 选品策略建议

3. **`outputs/reports/`**
   - 各平台详细数据报告

4. **`sources/[平台]/`**
   - 原始JSON数据存档

---

## ⚠️ 注意事项

1. **小红书/抖音**需要配置Cookie才能获取真实数据，当前为演示数据
2. 建议使用Selenium模式抓取动态页面
3. 注意控制请求频率，避免触发反爬
4. Cookie等敏感信息请使用 `.env` 配置

---

## 🔄 与Obsidian集成

本系统完全融入知识库三层架构：

```
sources/    ← 爬虫原始数据（只追加，不变）
  ↓
memory/     ← 编译后的SKILL、洞察、规律（可重写）
  ↓
outputs/    ← 分析报告（交付物）
```
