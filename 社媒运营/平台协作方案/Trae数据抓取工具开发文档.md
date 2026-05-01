# Trae 数据抓取工具开发文档

> 创建时间：2026-04-20
> 版本：v1.0
> 目标：为钟钟AIZz账号提供竞品数据支持

---

## 一、技术选型建议

### 1.1 核心语言与框架

| 组件 | 推荐选择 | 理由 |
|------|----------|------|
| **主语言** | Python 3.10+ | 生态丰富，爬虫库成熟，学习成本低 |
| **异步框架** | aiohttp + asyncio | 高并发，适合多商品同时抓取 |
| **HTML解析** | BeautifulSoup4 + lxml | 轻量易用，配合正则处理动态内容 |
| **数据存储** | JSON/CSV + SQLite | 轻量级存储，便于后续分析 |
| **API框架** | FastAPI | 与Coze对接简单，支持自动文档 |

### 1.2 反爬应对工具链

| 场景 | 工具 | 说明 |
|------|------|------|
| **IP代理** | proxypool / 芝麻代理 | 轮换IP，降低封禁风险 |
| **浏览器指纹** | undetected-chromedriver | 绕过检测，支持无头模式 |
| **验证码** | 超级鹰 / 打码平台 | 付费打码，处理滑块/图文验证码 |
| **请求限速** | asyncio + aiohttp | 控制并发，模拟人工访问 |
| **Cookie管理** | requests-session | 自动刷新Cookie，维持登录态 |

### 1.3 代理服务推荐

| 服务商 | 价格 | 特点 | 适用场景 |
|--------|------|------|----------|
| **芝麻代理** | ¥8/千IP | 量大稳定，支持HTTP/SOCKS5 | 1688、拼多多 |
| **阿布云** | ¥15/千IP | 独享IP，高匿 | 闲鱼（风控严） |
| **熊猫代理** | ¥5/千IP | 性价比高 | 初步测试 |

---

## 二、完整代码框架

### 2.1 项目结构

```
sources/scripts/crawler/
├── config/
│   └── settings.py           # 配置文件
├── core/
│   ├── base_crawler.py       # 基类
│   ├── proxy_manager.py      # 代理管理
│   └── storage.py            # 数据存储
├── platforms/
│   ├── __init__.py
│   ├── crawler_1688.py       # 1688爬虫
│   ├── crawler_xianyu.py     # 闲鱼爬虫
│   └── crawler_pinduoduo.py  # 拼多多爬虫
├── utils/
│   ├── http_client.py        # HTTP客户端
│   ├── parser.py             # 解析工具
│   └── logger.py             # 日志模块
├── api/
│   └── fastapi_server.py     # API服务（与Coze对接）
├── main.py                   # 主入口
├── requirements.txt          # 依赖
└── README.md                 # 使用说明
```

### 2.2 核心配置文件

```python
# config/settings.py
from pathlib import Path
from dataclasses import dataclass
import json

BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "outputs" / "crawler_data"

@dataclass
class CrawlerConfig:
    """爬虫通用配置"""
    # 请求间隔（秒）
    request_delay: float = 2.0
    # 最大重试次数
    max_retries: int = 3
    # 单次最大抓取数量
    max_per_page: int = 20
    # 请求超时（秒）
    timeout: int = 30
    # 并发数
    concurrency: int = 5

@dataclass
class PlatformConfig:
    """平台特定配置"""
    name: str
    base_url: str
    search_url: str
    headers: dict
    cookies: dict = None

# 1688配置
ALIBABA_CONFIG = PlatformConfig(
    name="1688",
    base_url="https://www.1688.com",
    search_url="https://s.1688.com/youyuan/index.htm?tab=sale&beginNum=0&pageSize=40",
    headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": "https://www.1688.com/",
    }
)

# 闲鱼配置
XIANYU_CONFIG = PlatformConfig(
    name="闲鱼",
    base_url="https://www.goofish.com",
    search_url="https://www.goofish.com/search?q=",
    headers={
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }
)

# 拼多多配置
PINDUODUO_CONFIG = PlatformConfig(
    name="拼多多",
    base_url="https://pinduoduo.com",
    search_url="https://mobile.yangkeduo.com/search_result.html?search_key=",
    headers={
        "User-Agent": "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "X-Requested-With": "com.xunmeng.pinduoduo",
    }
)

def load_proxies(filepath: str = None) -> list:
    """加载代理列表"""
    if filepath and Path(filepath).exists():
        with open(filepath, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    return []

def ensure_dirs():
    """确保目录存在"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "1688").mkdir(exist_ok=True)
    (DATA_DIR / "闲鱼").mkdir(exist_ok=True)
    (DATA_DIR / "拼多多").mkdir(exist_ok=True)
```

### 2.3 基类设计

```python
# core/base_crawler.py
import asyncio
import aiohttp
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
import json
import time
from core.storage import Storage
from core.proxy_manager import ProxyManager

class BaseCrawler(ABC):
    """爬虫基类"""
    
    def __init__(self, config, name: str):
        self.config = config
        self.name = name
        self.storage = Storage(name)
        self.proxy_manager = ProxyManager()
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        """异步上下文管理器"""
        connector = aiohttp.TCPConnector(limit=self.config.concurrency)
        self.session = aiohttp.ClientSession(
            connector=connector,
            headers=self.config.headers
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """关闭会话"""
        if self.session:
            await self.session.close()
    
    async def fetch(self, url: str, retries: int = None) -> Optional[str]:
        """带重试的HTTP请求"""
        retries = retries or self.config.max_retries
        
        for attempt in range(retries):
            try:
                proxy = self.proxy_manager.get_random_proxy()
                
                async with self.session.get(
                    url,
                    proxy=proxy,
                    timeout=aiohttp.ClientTimeout(total=self.config.timeout)
                ) as response:
                    if response.status == 200:
                        return await response.text()
                    elif response.status in [403, 429]:
                        # 被封禁，切换代理重试
                        self.proxy_manager.mark_failed(proxy)
                        await asyncio.sleep(self.config.request_delay * 2)
                    else:
                        print(f"[{self.name}] 请求失败: {response.status}")
                        
            except Exception as e:
                print(f"[{self.name}] 请求异常 (尝试 {attempt+1}/{retries}): {e}")
                await asyncio.sleep(self.config.request_delay)
                
        return None
    
    @abstractmethod
    async def search(self, keyword: str, pages: int = 1) -> List[Dict]:
        """搜索商品（子类实现）"""
        pass
    
    @abstractmethod
    async def parse_product(self, html: str) -> Dict:
        """解析商品详情（子类实现）"""
        pass
    
    async def run(self, keywords: List[str], pages: int = 1):
        """运行爬虫"""
        all_products = []
        
        async with self:
            for keyword in keywords:
                print(f"[{self.name}] 开始抓取关键词: {keyword}")
                products = await self.search(keyword, pages)
                all_products.extend(products)
                
                # 保存中间结果
                self.storage.save(products, f"{keyword}_{datetime.now():%Y%m%d}")
                
                # 限速
                await asyncio.sleep(self.config.request_delay)
        
        print(f"[{self.name}] 共抓取 {len(all_products)} 个商品")
        return all_products
```

### 2.4 1688爬虫实现

```python
# platforms/crawler_1688.py
import asyncio
import re
from typing import List, Dict
from bs4 import BeautifulSoup
from core.base_crawler import BaseCrawler
from config.settings import ALIBABA_CONFIG, CrawlerConfig

class Alibaba1688Crawler(BaseCrawler):
    """1688商品爬虫"""
    
    def __init__(self):
        super().__init__(ALIBABA_CONFIG, "1688")
        self.search_template = (
            "https://s.1688.com/youyuan/index.htm?"
            "tab=sale&beginNum=0&pageSize=40&sortType=st&keywords={keyword}&page={page}"
        )
    
    async def search(self, keyword: str, pages: int = 1) -> List[Dict]:
        """搜索1688商品"""
        products = []
        
        for page in range(1, pages + 1):
            url = self.search_template.format(keyword=keyword, page=page)
            print(f"[1688] 抓取第 {page}/{pages} 页: {keyword}")
            
            html = await self.fetch(url)
            if html:
                page_products = self.parse_product_list(html)
                products.extend(page_products)
                print(f"[1688] 第 {page} 页解析到 {len(page_products)} 个商品")
            
            await asyncio.sleep(self.config.request_delay)
        
        return products
    
    def parse_product_list(self, html: str) -> List[Dict]:
        """解析商品列表页"""
        products = []
        soup = BeautifulSoup(html, 'lxml')
        
        # 1688商品卡片选择器（需根据实际页面调整）
        cards = soup.select('.seb-product-item') or soup.select('.offer-list .offer')
        
        for card in cards:
            try:
                product = {
                    'platform': '1688',
                    'title': self._extract_text(card, '.title', '商品标题'),
                    'price': self._extract_price(card, '.price', '价格'),
                    'sales': self._extract_sales(card, '.sale-count', '销量'),
                    'shop': self._extract_text(card, '.shop-name', '店铺名'),
                    'location': self._extract_text(card, '.location', '地区'),
                    'url': self._extract_url(card, 'a', '链接'),
                    'image': self._extract_image(card, 'img', '图片'),
                    'crawl_time': datetime.now().isoformat(),
                }
                
                # 提取关键属性
                product.update(self._extract_attributes(card))
                
                if product['title']:
                    products.append(product)
                    
            except Exception as e:
                print(f"[1688] 解析商品异常: {e}")
                continue
        
        return products
    
    def _extract_text(self, soup, selector: str, field: str) -> str:
        """提取文本"""
        elem = soup.select_one(selector)
        return elem.get('title', '').strip() if elem else ''
    
    def _extract_price(self, soup, selector: str, field: str) -> str:
        """提取价格"""
        elem = soup.select_one(selector)
        if elem:
            price_text = elem.get_text(strip=True)
            # 提取数字
            match = re.search(r'[\d.]+', price_text)
            return match.group() if match else ''
        return ''
    
    def _extract_sales(self, soup, selector: str, field: str) -> str:
        """提取销量"""
        elem = soup.select_one(selector)
        if elem:
            text = elem.get_text(strip=True)
            match = re.search(r'(\d+)', text)
            return match.group(1) if match else '0'
        return '0'
    
    def _extract_url(self, soup, selector: str, field: str) -> str:
        """提取链接"""
        elem = soup.select_one(selector)
        if elem:
            return elem.get('href', '')
        return ''
    
    def _extract_image(self, soup, selector: str, field: str) -> str:
        """提取图片"""
        elem = soup.select_one(selector)
        if elem:
            return elem.get('src', '') or elem.get('data-src', '')
        return ''
    
    def _extract_attributes(self, card) -> Dict:
        """提取商品属性"""
        attrs = {}
        
        # 月销量
        sale_elem = card.select_one('[class*="sale"]')
        if sale_elem:
            attrs['monthly_sales'] = re.search(r'\d+', sale_elem.get_text()) or '0'
        
        # 起订量
        moq_elem = card.select_one('[class*="moq"]')
        if moq_elem:
            attrs['min_order'] = re.search(r'\d+', moq_elem.get_text()) or '1'
        
        return attrs
    
    async def parse_product(self, html: str) -> Dict:
        """解析商品详情页"""
        # 详情页解析逻辑（可选）
        pass
```

### 2.5 闲鱼爬虫实现

```python
# platforms/crawler_xianyu.py
import asyncio
import json
import re
from typing import List, Dict
from bs4 import BeautifulSoup
from core.base_crawler import BaseCrawler
from config.settings import XIANYU_CONFIG, CrawlerConfig

class XianyuCrawler(BaseCrawler):
    """闲鱼商品爬虫"""
    
    def __init__(self):
        super().__init__(XIANYU_CONFIG, "闲鱼")
        # 闲鱼API（需登录态，简化处理）
        self.api_template = (
            "https://guide.xianyu.com/api/search/item?"
            "keyword={keyword}&page={page}&pageSize=20"
        )
    
    async def search(self, keyword: str, pages: int = 1) -> List[Dict]:
        """搜索闲鱼商品"""
        products = []
        
        for page in range(1, pages + 1):
            # 闲鱼使用H5页面
            url = f"https://www.goofish.com/search?q={keyword}&page={page}"
            print(f"[闲鱼] 抓取第 {page}/{pages} 页: {keyword}")
            
            html = await self.fetch(url)
            if html:
                # 闲鱼页面通常有JSON数据嵌入
                page_products = self.parse_from_json(html)
                if not page_products:
                    page_products = self.parse_product_list(html)
                products.extend(page_products)
                print(f"[闲鱼] 第 {page} 页解析到 {len(page_products)} 个商品")
            
            await asyncio.sleep(self.config.request_delay * 1.5)  # 闲鱼风控更严
            
        return products
    
    def parse_from_json(self, html: str) -> List[Dict]:
        """从页面JSON中提取数据"""
        products = []
        
        # 匹配JSON数据
        match = re.search(r'window\.__INIT_PROPS__\s*=\s*({.+?})\s*</script>', html, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(1))
                items = data.get('items', []) or data.get('result', {}).get('items', [])
                
                for item in items:
                    product = {
                        'platform': '闲鱼',
                        'title': item.get('title', ''),
                        'price': str(item.get('price', 0)),
                        'location': item.get('location', ''),
                        'shop': item.get('sellerNick', ''),
                        'sales': item.get('sold', 0),
                        'url': f"https://www.goofish.com/item?id={item.get('id', '')}",
                        'image': item.get('image', ''),
                        'crawl_time': datetime.now().isoformat(),
                    }
                    products.append(product)
                    
            except json.JSONDecodeError:
                pass
        
        return products
    
    def parse_product_list(self, html: str) -> List[Dict]:
        """解析商品列表页（备选方案）"""
        products = []
        soup = BeautifulSoup(html, 'lxml')
        
        # 闲鱼H5页面选择器
        items = soup.select('.feed-item') or soup.select('[class*="item"]')
        
        for item in items:
            try:
                product = {
                    'platform': '闲鱼',
                    'title': item.select_one('.title, [class*="title"]').get_text(strip=True) if item.select_one('.title, [class*="title"]') else '',
                    'price': item.select_one('.price, [class*="price"]').get_text(strip=True) if item.select_one('.price, [class*="price"]') else '',
                    'location': item.select_one('[class*="location"]').get_text(strip=True) if item.select_one('[class*="location"]') else '',
                    'shop': item.select_one('[class*="seller"]').get_text(strip=True) if item.select_one('[class*="seller"]') else '',
                    'url': item.select_one('a').get('href', '') if item.select_one('a') else '',
                    'image': item.select_one('img').get('src', '') if item.select_one('img') else '',
                    'crawl_time': datetime.now().isoformat(),
                }
                
                if product['title']:
                    products.append(product)
                    
            except Exception as e:
                print(f"[闲鱼] 解析异常: {e}")
                continue
        
        return products
```

### 2.6 拼多多爬虫实现

```python
# platforms/crawler_pinduoduo.py
import asyncio
import hashlib
import json
import re
from typing import List, Dict
from bs4 import BeautifulSoup
from core.base_crawler import BaseCrawler
from config.settings import PINDUODUO_CONFIG, CrawlerConfig

class PinduoduoCrawler(BaseCrawler):
    """拼多多商品爬虫"""
    
    def __init__(self):
        super().__init__(PINDUODUO_CONFIG, "闲鱼")
        self.search_url_template = (
            "https://mobile.yangkeduo.com/search_result.html?"
            "search_key={keyword}&page={page}&size=20"
        )
    
    async def search(self, keyword: str, pages: int = 1) -> List[Dict]:
        """搜索拼多多商品"""
        products = []
        
        for page in range(1, pages + 1):
            url = self.search_url_template.format(keyword=keyword, page=page)
            print(f"[拼多多] 抓取第 {page}/{pages} 页: {keyword}")
            
            html = await self.fetch(url)
            if html:
                page_products = self.parse_product_list(html)
                products.extend(page_products)
                print(f"[拼多多] 第 {page} 页解析到 {len(page_products)} 个商品")
            
            await asyncio.sleep(self.config.request_delay * 1.2)
        
        return products
    
    def parse_product_list(self, html: str) -> List[Dict]:
        """解析商品列表页"""
        products = []
        soup = BeautifulSoup(html, 'lxml')
        
        # 拼多多H5页面选择器
        items = soup.select('.goods-item') or soup.select('[class*="goods"]')
        
        for item in items:
            try:
                product = {
                    'platform': '拼多多',
                    'title': self._safe_get_text(item, '.goods-title, [class*="title"]'),
                    'price': self._extract_price(item),
                    'sales': self._extract_sales_pdd(item),
                    'shop': self._safe_get_text(item, '.mall-name, [class*="mall"]'),
                    'location': '',  # 拼多多通常不显示位置
                    'url': self._safe_get_attr(item, 'a', 'href'),
                    'image': self._safe_get_attr(item, 'img', 'src'),
                    'crawl_time': datetime.now().isoformat(),
                }
                
                # 提取评分/补贴信息
                product['has_subsidy'] = bool(item.select('[class*="subsidy"]'))
                product['rank'] = self._safe_get_text(item, '[class*="rank"]')
                
                if product['title']:
                    products.append(product)
                    
            except Exception as e:
                print(f"[拼多多] 解析异常: {e}")
                continue
        
        return products
    
    def _safe_get_text(self, soup, selector: str) -> str:
        """安全获取文本"""
        elem = soup.select_one(selector)
        return elem.get_text(strip=True) if elem else ''
    
    def _safe_get_attr(self, soup, selector: str, attr: str) -> str:
        """安全获取属性"""
        elem = soup.select_one(selector)
        return elem.get(attr, '') if elem else ''
    
    def _extract_price(self, soup) -> str:
        """提取价格"""
        price_elem = soup.select_one('[class*="price"]')
        if price_elem:
            text = price_elem.get_text(strip=True)
            match = re.search(r'[\d.]+', text)
            return match.group() if match else ''
        return ''
    
    def _extract_sales_pdd(self, soup) -> str:
        """提取拼多多销量"""
        sales_elem = soup.select_one('[class*="sales"]') or soup.select_one('[class*="sold"]')
        if sales_elem:
            text = sales_elem.get_text(strip=True)
            # 转换"万人拼"等格式
            match = re.search(r'([\d.]+)\s*[万]?人', text)
            if match:
                num = float(match.group(1))
                if '万' in text:
                    num *= 10000
                return str(int(num))
            match = re.search(r'(\d+)', text)
            return match.group(1) if match else '0'
        return '0'
```

### 2.7 数据存储模块

```python
# core/storage.py
import json
import csv
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import sqlite3

class Storage:
    """数据存储模块"""
    
    def __init__(self, platform: str):
        self.platform = platform
        self.base_dir = Path(__file__).parent.parent.parent / "outputs" / "crawler_data" / platform
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def save(self, data: List[Dict], filename: str) -> str:
        """保存数据（JSON格式）"""
        filepath = self.base_dir / f"{filename}.json"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"[Storage] 保存到 {filepath}，共 {len(data)} 条记录")
        return str(filepath)
    
    def save_csv(self, data: List[Dict], filename: str) -> str:
        """保存为CSV格式"""
        if not data:
            return ""
        
        filepath = self.base_dir / f"{filename}.csv"
        
        # 获取所有字段
        fieldnames = list(data[0].keys())
        
        with open(filepath, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        
        print(f"[Storage] 保存CSV到 {filepath}，共 {len(data)} 条记录")
        return str(filepath)
    
    def save_sqlite(self, data: List[Dict], table_name: str = "products"):
        """保存到SQLite数据库"""
        db_path = self.base_dir / f"{self.platform}.db"
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        if data:
            # 创建表
            columns = list(data[0].keys())
            column_defs = [f'"{col}" TEXT' for col in columns]
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    {', '.join(column_defs)},
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 插入数据
            placeholders = ', '.join(['?'] * len(columns))
            cursor.executemany(
                f'INSERT INTO {table_name} ({", ".join(columns)}) VALUES ({placeholders})',
                [tuple(item.get(col, '') for col in columns) for item in data]
            )
            
            conn.commit()
        
        conn.close()
        print(f"[Storage] 保存到SQLite: {db_path}")
        return str(db_path)
    
    def load(self, filename: str) -> List[Dict]:
        """加载JSON数据"""
        filepath = self.base_dir / f"{filename}.json"
        
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
```

### 2.8 代理管理模块

```python
# core/proxy_manager.py
import random
import requests
from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Proxy:
    ip: str
    port: int
    protocol: str = 'http'
    success_count: int = 0
    fail_count: int = 0
    last_used: datetime = None
    
    @property
    def url(self) -> str:
        return f"{self.protocol}://{self.ip}:{self.port}"

class ProxyManager:
    """代理池管理"""
    
    def __init__(self, api_url: str = None, proxy_file: str = None):
        self.api_url = api_url  # 代理服务商API
        self.proxy_file = proxy_file
        self.proxies: List[Proxy] = []
        self.current_index = 0
        self.failed_proxies = set()
        
        self._load_proxies()
    
    def _load_proxies(self):
        """加载代理列表"""
        if self.api_url:
            try:
                response = requests.get(self.api_url)
                if response.status_code == 200:
                    for line in response.text.strip().split('\n'):
                        parts = line.strip().split(':')
                        if len(parts) == 4:
                            self.proxies.append(Proxy(
                                ip=parts[0],
                                port=int(parts[1]),
                                protocol=parts[2],
                                password=parts[3]
                            ))
            except Exception as e:
                print(f"[ProxyManager] API获取代理失败: {e}")
        
        if self.proxy_file:
            with open(self.proxy_file, 'r') as f:
                for line in f:
                    parts = line.strip().split(':')
                    if len(parts) >= 2:
                        self.proxies.append(Proxy(
                            ip=parts[0],
                            port=int(parts[1])
                        ))
        
        print(f"[ProxyManager] 加载了 {len(self.proxies)} 个代理")
    
    def get_random_proxy(self) -> Optional[str]:
        """获取随机代理"""
        available = [p for p in self.proxies 
                     if p.url not in self.failed_proxies]
        
        if not available:
            # 如果全部失败，重置失败列表
            self.failed_proxies.clear()
            available = self.proxies
        
        if available:
            proxy = random.choice(available)
            proxy.last_used = datetime.now()
            return proxy.url
        
        return None
    
    def mark_failed(self, proxy_url: str):
        """标记失败的代理"""
        self.failed_proxies.add(proxy_url)
        
        # 从活跃列表移除
        for p in self.proxies:
            if p.url == proxy_url:
                p.fail_count += 1
                break
        
        print(f"[ProxyManager] 代理 {proxy_url} 标记失败，当前失败数: {len(self.failed_proxies)}")
    
    def mark_success(self, proxy_url: str):
        """标记成功的代理"""
        for p in self.proxies:
            if p.url == proxy_url:
                p.success_count += 1
                break
```

### 2.9 主入口文件

```python
# main.py
import asyncio
import argparse
from datetime import datetime
from pathlib import Path
import sys

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import CrawlerConfig
from platforms.crawler_1688 import Alibaba1688Crawler
from platforms.crawler_xianyu import XianyuCrawler
from platforms.crawler_pinduoduo import PinduoduoCrawler

async def main():
    parser = argparse.ArgumentParser(description='电商数据爬虫')
    parser.add_argument('--platform', '-p', choices=['1688', 'xianyu', 'pinduoduo', 'all'],
                        default='all', help='选择平台')
    parser.add_argument('--keywords', '-k', nargs='+', 
                        default=['AI工具', '智能助手', '效率软件'],
                        help='搜索关键词')
    parser.add_argument('--pages', '-n', type=int, default=2,
                        help='抓取页数')
    
    args = parser.parse_args()
    
    config = CrawlerConfig(
        request_delay=2.0,
        max_retries=3,
        concurrency=5,
        timeout=30
    )
    
    crawlers = {
        '1688': Alibaba1688Crawler,
        'xianyu': XianyuCrawler,
        'pinduoduo': PinduoduoCrawler,
    }
    
    all_results = {}
    
    platforms = crawlers.keys() if args.platform == 'all' else [args.platform]
    
    for platform in platforms:
        print(f"\n{'='*50}")
        print(f"开始抓取 {platform}")
        print(f"{'='*50}")
        
        crawler_class = crawlers[platform]
        crawler = crawler_class()
        
        results = await crawler.run(args.keywords, args.pages)
        all_results[platform] = results
        
        # 每个平台间隔，避免连续请求
        await asyncio.sleep(3)
    
    # 汇总报告
    print(f"\n{'='*50}")
    print("抓取完成汇总")
    print(f"{'='*50}")
    for platform, results in all_results.items():
        print(f"{platform}: {len(results)} 个商品")
    
    return all_results

if __name__ == '__main__':
    asyncio.run(main())
```

---

## 三、反爬应对策略

### 3.1 策略矩阵

| 平台 | 风控等级 | 主要策略 |
|------|----------|----------|
| **1688** | ⭐⭐⭐ 中 | UA检测、IP频率限制、Cookie验证 |
| **闲鱼** | ⭐⭐⭐⭐ 高 | UA指纹、设备指纹、行为分析、验证码 |
| **拼多多** | ⭐⭐⭐⭐ 高 | 设备指纹、APP签名、IP频率限制 |

### 3.2 详细应对方案

#### 策略1：User-Agent轮换

```python
# core/http_client.py
import random

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
]

def get_random_headers():
    """获取随机请求头"""
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }
    return headers
```

#### 策略2：代理IP池

```python
# 使用芝麻代理示例
ZHUIMA_API = "http://api.zmhttp.com/getip?num=50&type=2&pack=YOUR_PACK_ID&port=1&nowrap=1"

class ProxyPool:
    def __init__(self):
        self.proxies = []
        self.index = 0
        self.refresh()
    
    def refresh(self):
        """刷新代理"""
        try:
            resp = requests.get(ZHUIMA_API, timeout=10)
            if resp.status_code == 200:
                self.proxies = [
                    f"http://{line.strip()}"
                    for line in resp.text.strip().split('\n')
                    if line.strip()
                ]
                self.index = 0
                print(f"[ProxyPool] 刷新成功，获得 {len(self.proxies)} 个代理")
        except Exception as e:
            print(f"[ProxyPool] 刷新失败: {e}")
    
    def get(self):
        """获取代理"""
        if not self.proxies or self.index >= len(self.proxies):
            self.refresh()
        
        proxy = self.proxies[self.index]
        self.index += 1
        return proxy
```

#### 策略3：浏览器指纹（高级）

```python
# 使用undetected-chromedriver（闲鱼/拼多多推荐）
import undetected_chromedriver as uc

class BrowserCrawler:
    def __init__(self):
        options = uc.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        self.driver = uc.Chrome(options=options, version_main=120)
    
    def search(self, url):
        self.driver.get(url)
        # 模拟滚动
        for _ in range(3):
            self.driver.execute_script("window.scrollBy(0, 500)")
            time.sleep(1)
        
        return self.driver.page_source
    
    def close(self):
        self.driver.quit()
```

#### 策略4：验证码处理

```python
# 超级鹰打码平台集成
import base64
import requests

class CaptchaSolver:
    def __init__(self, username, password, soft_id='soft_id'):
        self.username = username
        self.password = password
        self.soft_id = soft_id
        self.api_url = "http://api.chaojiying.net/Upload/Processing.php"
    
    def solve(self, image_path, codetype='5000'):
        """识别验证码"""
        with open(image_path, 'rb') as f:
            img_data = base64.b64encode(f.read()).decode()
        
        data = {
            'user': self.username,
            'pass2': self.password,
            'softid': self.soft_id,
            'codetype': codetype,
            'userfile': img_data,
        }
        
        resp = requests.post(self.api_url, data=data)
        result = resp.json()
        
        if result['err_str'] == 'OK':
            return result['pic_str']
        else:
            raise Exception(f"打码失败: {result['err_str']}")
```

### 3.3 请求频率控制

```python
class RateLimiter:
    """令牌桶限流器"""
    
    def __init__(self, rate: float, capacity: int):
        self.rate = rate  # 每秒生成令牌数
        self.capacity = capacity  # 桶容量
        self.tokens = capacity
        self.last_update = time.time()
    
    def acquire(self):
        """获取令牌"""
        now = time.time()
        elapsed = now - self.last_update
        
        # 补充令牌
        self.tokens = min(
            self.capacity,
            self.tokens + elapsed * self.rate
        )
        self.last_update = now
        
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        else:
            return False
    
    async def wait_and_acquire(self):
        """等待获取令牌"""
        while not self.acquire():
            await asyncio.sleep(0.1)

# 使用示例
rate_limiter = RateLimiter(rate=0.5, capacity=3)  # 每2秒1个请求，最多堆积3个

async def throttled_request(url):
    await rate_limiter.wait_and_acquire()
    return await fetch(url)
```

---

## 四、数据输出格式

### 4.1 标准JSON输出

```json
{
  "platform": "1688",
  "keyword": "AI智能助手",
  "crawl_time": "2026-04-20T14:30:00+08:00",
  "page": 1,
  "total_count": 40,
  "products": [
    {
      "id": "168800123456",
      "title": "AI智能客服机器人 语音交互 电商客服 24小时在线",
      "price": "2999.00",
      "currency": "CNY",
      "unit": "台",
      "sales": "856",
      "monthly_sales": "123",
      "shop": {
        "name": "深圳市XX科技有限公司",
        "type": "源头工厂",
        "rating": "4.8"
      },
      "location": {
        "province": "广东",
        "city": "深圳"
      },
      "min_order": 1,
      "images": [
        "https://img.alicdn.com/xxx.jpg"
      ],
      "url": "https://detail.1688.com/offer/168800123456.html",
      "has_video": true,
      "attributes": {
        "品牌": "XX品牌",
        "产地": "深圳"
      }
    }
  ]
}
```

### 4.2 汇总CSV格式

```csv
platform,keyword,title,price,sales,shop_name,shop_type,location,min_order,url,crawl_time
1688,AI工具,AI智能客服机器人,2999,856,深圳市XX科技,源头工厂,广东深圳,1,https://...,2026-04-20
1688,AI工具,智能语音助手,1999,432,杭州XX智能,普通店铺,浙江杭州,10,https://...,2026-04-20
```

### 4.3 数据库Schema

```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform VARCHAR(20),           -- 平台
    external_id VARCHAR(50),         -- 平台商品ID
    title TEXT,                      -- 商品标题
    price DECIMAL(10,2),             -- 价格
    currency VARCHAR(5),             -- 货币
    sales INTEGER DEFAULT 0,         -- 总销量
    monthly_sales INTEGER DEFAULT 0, -- 月销量
    shop_name VARCHAR(100),         -- 店铺名
    shop_type VARCHAR(20),          -- 店铺类型
    location VARCHAR(50),           -- 地区
    min_order INTEGER DEFAULT 1,     -- 最小起订量
    url TEXT,                        -- 商品链接
    image_url TEXT,                  -- 主图链接
    has_video BOOLEAN DEFAULT FALSE, -- 是否有视频
    crawl_time DATETIME,             -- 抓取时间
    keywords TEXT,                   -- 关联关键词(JSON数组)
    attributes TEXT                  -- 属性JSON
);

CREATE INDEX idx_platform ON products(platform);
CREATE INDEX idx_sales ON products(sales DESC);
CREATE INDEX idx_crawl_time ON products(crawl_time);
```

---

## 五、与Coze对接方式

### 5.1 API服务设计

```python
# api/fastapi_server.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import asyncio

app = FastAPI(title="电商数据爬虫API")

class CrawlRequest(BaseModel):
    """抓取请求"""
    platform: str  # 1688, xianyu, pinduoduo
    keywords: List[str]
    pages: int = 1

class CrawlResponse(BaseModel):
    """抓取响应"""
    task_id: str
    status: str
    message: str

class TaskResult(BaseModel):
    """任务结果"""
    task_id: str
    status: str  # pending, running, completed, failed
    results: Optional[List[dict]]
    error: Optional[str]

# 任务存储（实际使用Redis）
tasks = {}

@app.post("/crawl", response_model=CrawlResponse)
async def start_crawl(request: CrawlRequest):
    """启动抓取任务"""
    task_id = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{request.platform}"
    
    tasks[task_id] = {
        "status": "pending",
        "request": request.dict(),
        "results": None
    }
    
    # 异步执行抓取
    asyncio.create_task(run_crawl(task_id, request))
    
    return CrawlResponse(
        task_id=task_id,
        status="pending",
        message=f"任务已创建，将在后台执行"
    )

@app.get("/task/{task_id}", response_model=TaskResult)
async def get_task_result(task_id: str):
    """查询任务结果"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, message="任务不存在")
    
    task = tasks[task_id]
    return TaskResult(
        task_id=task_id,
        status=task["status"],
        results=task.get("results"),
        error=task.get("error")
    )

@app.get("/tasks")
async def list_tasks():
    """列出所有任务"""
    return [
        {"task_id": k, "status": v["status"], "created_at": v.get("created_at")}
        for k, v in tasks.items()
    ]

async def run_crawl(task_id: str, request: CrawlRequest):
    """执行抓取任务"""
    tasks[task_id]["status"] = "running"
    tasks[task_id]["created_at"] = datetime.now().isoformat()
    
    try:
        # 导入爬虫（延迟导入避免循环）
        from platforms.crawler_1688 import Alibaba1688Crawler
        from platforms.crawler_xianyu import XianyuCrawler
        from platforms.crawler_pinduoduo import PinduoduoCrawler
        
        crawlers = {
            "1688": Alibaba1688Crawler,
            "xianyu": XianyuCrawler,
            "pinduoduo": PinduoduoCrawler,
        }
        
        crawler_class = crawlers.get(request.platform)
        if not crawler_class:
            raise ValueError(f"不支持的平台: {request.platform}")
        
        crawler = crawler_class()
        results = await crawler.run(request.keywords, request.pages)
        
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["results"] = results
        
    except Exception as e:
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["error"] = str(e)

# 健康检查
@app.get("/health")
async def health():
    return {"status": "ok", "time": datetime.now().isoformat()}
```

### 5.2 Coze调用方式

#### 方式1：HTTP回调（推荐）

```python
# Coze端使用API调用
import requests

def trigger_crawl(platform: str, keywords: list, callback_url: str = None):
    """触发爬虫任务"""
    api_url = "http://your-server:8000/crawl"
    
    payload = {
        "platform": platform,
        "keywords": keywords,
        "pages": 2
    }
    
    response = requests.post(api_url, json=payload)
    result = response.json()
    
    return result  # 返回 task_id

# 获取结果
def get_crawl_result(task_id: str):
    """获取抓取结果"""
    api_url = f"http://your-server:8000/task/{task_id}"
    
    response = requests.get(api_url)
    return response.json()
```

#### 方式2：WebSocket实时推送

```python
# api/websocket_server.py
import asyncio
import websockets
import json
from fastapi import WebSocket

connected_clients = set()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    connected_clients.add(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            # 处理客户端消息
            message = json.loads(data)
            
            if message["type"] == "subscribe":
                # 订阅特定任务
                pass
                
    except websockets.exceptions.ConnectionClosed:
        connected_clients.remove(websocket)

async def notify_clients(task_id: str, result: dict):
    """向订阅的客户端推送结果"""
    message = json.dumps({
        "type": "task_complete",
        "task_id": task_id,
        "data": result
    })
    
    for client in connected_clients:
        try:
            await client.send_text(message)
        except:
            pass
```

### 5.3 云电脑部署配置

```bash
# 部署到云电脑(Ubuntu 22.04)
# 1. 安装依赖
apt update && apt install python3.10 python3-pip git
pip3 install fastapi uvicorn aiohttp beautifulsoup4 lxml aiofiles

# 2. 上传代码（使用scp或git）
scp -r ./crawler user@cloud-pc:/home/user/crawler

# 3. 配置服务
sudo nano /etc/systemd/system/crawler-api.service

[Unit]
Description=Crawler API Service
After=network.target

[Service]
Type=simple
User=user
WorkingDirectory=/home/user/crawler
ExecStart=/usr/bin/python3 /home/user/crawler/api/fastapi_server.py
Restart=always

[Install]
WantedBy=multi-user.target

# 4. 启动服务
sudo systemctl enable crawler-api
sudo systemctl start crawler-api

# 5. 验证
curl http://localhost:8000/health
```

---

## 六、requirements.txt

```
aiohttp==3.9.1
aiofiles==23.2.1
beautifulsoup4==4.12.2
lxml==5.0.0
requests==2.31.0
fastapi==0.109.0
uvicorn==0.27.0
pydantic==2.5.3
python-multipart==0.0.6
websockets==12.0
sqlite3 (内置)
```

---

> 📌 **使用说明**
> 1. 在Trae IDE中创建项目，复制代码框架
> 2. 配置代理API（芝麻代理或其他）
> 3. 先测试单平台单关键词，确认能抓取后扩展
> 4. 部署FastAPI服务到云电脑
> 5. Coze通过HTTP调用获取数据
