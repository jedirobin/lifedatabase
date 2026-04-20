# 🏗️ GrabLab 系统架构设计 v1.0

> 专业级多平台爬虫 + 知识库系统架构

---

## 🎯 功能优先级矩阵

| 功能 | 描述 | 优先级 | 状态 |
|------|------|--------|------|
| **关键词搜索** | 按关键词搜索内容/商品 | **P0** | ✅ 已实现 |
| **榜单抓取** | 抓取热门榜单、热销榜单 | **P0** | ✅ 已实现 |
| **详情抓取** | 抓取单个内容/商品详情 | **P0** | 规划中 |
| **评论抓取** | 抓取评论/弹幕数据 | **P0** | 规划中 |
| **批量抓取** | 支持批量抓取多个目标 | **P0** | ✅ WebUI已支持 |
| **增量更新** | 只抓取新增数据 | P1 | 规划中 |
| **定时任务** | 定时自动执行抓取 | P1 | ✅ 已实现 |
| **代理轮换** | 自动切换代理防封 | P1 | 规划中 |
| **验证码处理** | 自动/人工处理验证码 | P1 | 规划中 |

---

## 🧩 核心模块设计

### 1. 反爬策略处理器 AntiCrawlerHandler

```python
class AntiCrawlerHandler:
    """反爬策略处理器 - 高并发场景下自动规避反爬检测"""
    
    def __init__(self):
        self.proxy_pool = ProxyPool()           # 代理IP池
        self.user_agent_pool = UserAgentPool()  # UA随机池
        self.cookie_manager = CookieManager()   # Cookie自动管理
        self.request_limiter = RequestLimiter() # 智能限流
    
    def get_random_delay(self):
        """智能随机延迟，模拟人类浏览行为"""
        return random.uniform(0.8, 4.5)
    
    def rotate_proxy(self):
        """自动轮换代理IP"""
        pass
    
    def handle_captcha(self, captcha_type):
        """统一验证码处理
        - 滑块验证码
        - 点选验证码  
        - 文字验证码
        """
        pass
    
    def simulate_mouse_movement(self):
        """模拟真实鼠标移动轨迹 (贝塞尔曲线)"""
        pass
    
    def fingerprint_randomization(self):
        """浏览器指纹随机化，避免设备特征被识别"""
        pass
```

---

### 2. 登录管理器 LoginManager

```python
class LoginManager:
    """统一登录管理器 - 全平台多模式登录支持"""
    
    def __init__(self, platform):
        self.platform = platform
        self.cookies = None
        self.token = None
        self.session_expire = None
    
    def login_with_cookie(self, cookie_file):
        """Cookie导入登录（推荐）"""
        pass
    
    def login_with_qrcode(self):
        """扫码登录（浏览器弹出二维码）"""
        pass
    
    def login_with_sms(self, phone):
        """短信验证登录"""
        pass
    
    def save_session(self):
        """自动保存登录状态到本地"""
        pass
    
    def refresh_session(self):
        """会话过期自动刷新，无需重复登录"""
        pass
```

---

## 💾 数据存储规范

### 文件命名标准

```
{平台}_{数据类型}_{日期}_{批次号}.{后缀}
```

**示例：**
| 文件名 | 说明 |
|--------|------|
| `douyin_video_detail_20260420_001.json` | 抖音视频详情 |
| `xianyu_product_list_20260420_001.json` | 闲鱼商品列表 |
| `1688_hot_products_20260420_001.csv` | 1688热销榜单 |
| `bilibili_comments_20260420_001.json` | B站评论数据 |

### 文件格式规范

| 格式 | 适用场景 | 说明 |
|------|---------|------|
| **JSON** | 结构化数据 | 主要格式，便于AI解析和入库 |
| **CSV** | 表格数据 | 商品列表、销量数据、统计报表 |
| **Markdown** | 分析报告 | 生成SKILL文档、选品分析报告 |
| **SQLite** | 大量数据 | 超过10万条以上数据本地存储 |

---

## 📁 Obsidian 知识库目录结构

```
Obsidian Lifedatabase/
├── 📂 sources/
│   ├── 📱 抖音/
│   │   ├── 视频原始数据/
│   │   ├── 评论弹幕/
│   │   └── 热搜榜单/
│   ├── 📕 小红书/
│   │   ├── 笔记数据/
│   │   ├── 评论数据/
│   │   └── 话题热搜/
│   ├── 🎮 B站/
│   │   ├── 视频数据/
│   │   ├── 弹幕数据/
│   │   └── 热门榜单/
│   ├── 🐟 闲鱼/
│   │   ├── 商品数据/
│   │   └── 销量追踪/
│   ├── 🏪 1688/
│   │   ├── 商品数据/
│   │   ├── 批发价格/
│   │   └── 工厂信息/
│   └── 🛒 拼多多/
│       └── 商品数据/
│
├── 📂 memory/
│   ├── 📚 insights/          # 爆款创作SKILL
│   ├── 📊 product_research/  # 选品分析报告
│   ├── 🔥 hot_tracking/      # 热点追踪
│   └── schema.md             # 全局数据结构
│
└── 📂 outputs/
    ├── 📋 reports/           # 详细分析报告
    ├── 📈 dashboards/        # 可视化看板
    └── SKILL文档库/
```

---

## 🔄 数据流转 Pipeline

```
┌────────────┐    ┌────────────────┐    ┌────────────────┐    ┌────────────────┐
│  平台入口  │ →  │ 反爬策略模块   │ →  │ 数据标准化模块 │ →  │ 智能分析模块   │
└────────────┘    └────────────────┘    └────────────────┘    └────────────────┘
                                                            ↓
                                                    ┌────────────────┐
                                                    │ Obsidian 知识库 │
                                                    │   + NLP分析     │
                                                    │   + 向量检索    │
                                                    └────────────────┘
```

---

## 📊 模块实现进度

| 模块 | 功能 | 进度 |
|------|------|------|
| **基础爬虫框架** | 多平台统一基类 | ✅ 100% |
| **B站爬虫** | 热门+搜索 | ✅ 100% |
| **抖音/小红书爬虫** | 热门+搜索 | ✅ 100% |
| **内容分析引擎** | NLP关键词提取 | ✅ 100% |
| **电商选品** | 利润计算 | ✅ 100% |
| **WebUI界面** | Gradio操作界面 | ✅ 100% |
| **数据标准化** | Schema统一 | ✅ 100% |
| **Obsidian同步** | 自动写入知识库 | ✅ 100% |
| **Cookie管理** | .env配置 | ✅ 100% |
| **定时任务** | schedule调度 | ✅ 100% |
| **反爬模块** | 代理+验证码 | ⏳ 开发中 |
| **评论抓取** | 评论+弹幕NLP | ⏳ 规划中 |
| **详情深度抓取** | 内容结构化分析 | ⏳ 规划中 |

---

## 🚀 下一阶段里程碑

### Phase 1 - 已完成 ✅
- [x] 基础爬虫架构
- [x] 三大社媒平台爬虫
- [x] 数据标准化Schema
- [x] WebUI操作界面
- [x] Cookie配置体系
- [x] Obsidian自动同步

### Phase 2 - 进行中 🏗️
- [ ] 闲鱼/1688/拼多多爬虫
- [ ] 反爬策略模块
- [ ] 登录会话管理

### Phase 3 - 规划中 📋
- [ ] 评论+弹幕深度抓取
- [ ] 内容多维度结构化分析
- [ ] 代理IP池
- [ ] 向量相似度检索

---

*本架构文档持续更新中...*
