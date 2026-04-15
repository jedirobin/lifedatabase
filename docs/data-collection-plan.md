# 数据采集技术方案

> 本文档规划社交媒体数据采集的技术选型，不包含实现代码

---

## 一、B站 (Bilibili) 数据采集

### 1.1 官方API方案

**接口**：
- 用户信息：`https://api.bilibili.com/x/web-interface/card`
- 视频列表：`https://api.bilibili.com/x/space/arc/search`
- 视频详情：`https://api.bilibili.com/x/web-interface/view`

**优势**：
- 速度快，直接返回JSON
- 无需登录即可获取部分数据
- 官方支持

**限制**：
- 部分接口需要登录态
- 请求频率限制
- 用户隐私设置会隐藏内容

**适用场景**：用户公开视频列表、播放量、点赞数

### 1.2 第三方库方案

**推荐库**：`bilibili-api` (Python)

```python
from bilibili_api import user, video

# 获取用户信息
u = user.User(uid=123456)
info = await u.get_user_info()
```

**优势**：
- 封装完整，维护活跃
- 支持登录态操作
- 包含实时弹幕、评论等

**限制**：
- 需要处理风控
- 维护成本较高

### 1.3 推荐方案

| 场景 | 推荐方案 | 理由 |
|------|----------|------|
| 公开数据统计 | 官方API | 简单稳定 |
| 评论/弹幕采集 | bilibili-api | 功能完整 |
| 批量采集 | 官方API + 代理池 | 规避限流 |

---

## 二、抖音 (Douyin) 数据采集

### 2.1 浏览器自动化方案

**工具选择**：
- Playwright（推荐）
- Puppeteer
- Selenium

**优势**：
- 模拟真实用户行为
- 能获取登录态内容
- 反爬难度高

**限制**：
- 速度慢（需等待页面加载）
- 资源占用高
- IP容易被封

### 2.2 API抓包方案

**方法**：
1. Fiddler/Charles 抓包App请求
2. 分析加密参数
3. 重放请求

**优势**：
- 速度快
- 数据完整

**限制**：
- 加密算法可能更新
- 法律风险
- 实现复杂

### 2.3 推荐方案

| 场景 | 推荐方案 | 理由 |
|------|----------|------|
| 公开视频列表 | 官方网页版API | 无需复杂反爬 |
| 登录态内容 | Playwright自动化 | 稳定可靠 |
| 竞品监控 | API + 代理池 | 规模化 |

### 2.4 反爬策略应对

1. **请求间隔**：随机1-3秒
2. **User-Agent轮换**：模拟不同设备
3. **IP代理池**：避免单IP高频
4. **Cookie复用**：维持登录态

---

## 三、小红书 (Xiaohongshu) 数据采集

### 3.1 浏览器自动化方案

**特点**：
- 小红书反爬较强
- 建议使用手机UA模拟
- 需要处理滑块验证

**工具**：Playwright (推荐)

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    context = browser.new_context(
        user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)...'
    )
```

### 3.2 移动端API方案

**方法**：
1. 手机安装代理工具（如HttpCanary）
2. 抓包小红书App请求
3. 提取接口签名算法

**优势**：
- 数据完整
- 绕过部分反爬

**限制**：
- 实现复杂
- 算法可能更新

### 3.3 推荐方案

| 场景 | 推荐方案 | 理由 |
|------|----------|------|
| 笔记列表 | Playwright | 稳定 |
| 笔记详情 | Playwright + API | 混合 |
| 搜索结果 | API抓包 | 快速 |

### 3.4 注意事项

1. 小红书对IP变化敏感，建议固定IP
2. 登录态有效期较短，需定期更新Cookie
3. 大量采集建议使用云手机方案

---

## 四、技术架构建议

### 4.1 采集架构

```
┌─────────────┐
│  调度器     │  定时任务管理
└──────┬──────┘
       │
┌──────▼──────┐
│  采集器池   │  并发控制
├─────────────┤
│ B站采集器   │
│ 抖音采集器  │
│ 小红书采集器│
└──────┬──────┘
       │
┌──────▼──────┐
│  存储层     │  文件 + SQLite
└─────────────┘
```

### 4.2 文件存储结构

```
sources/
├── bilibili/
│   ├── users/{uid}/
│   │   ├── profile.json
│   │   └── videos/
│   └── videos/{bvid}/
│       ├── info.json
│       └── comments.json
├── douyin/
│   └── users/{uid}/
│       ├── profile.json
│       └── videos/
└── xiaohongshu/
    └── users/{user_id}/
        ├── profile.json
        └── notes/
```

### 4.3 采集频率建议

| 平台 | 频率 | 理由 |
|------|------|------|
| B站 | 每6小时 | 数据变化较快 |
| 抖音 | 每12小时 | 视频热度衰减慢 |
| 小红书 | 每24小时 | 更新频率适中 |

---

## 五、后续行动计划

- [ ] Phase1：单平台采集脚本（选一个平台先跑通）
- [ ] Phase2：多平台扩展
- [ ] Phase3：采集调度系统
- [ ] Phase4：数据可视化看板

---

*方案创建于: 2024*
*最后更新: 2024*
