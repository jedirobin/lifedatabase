import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent
ROOT_DIR = BASE_DIR.parent

load_dotenv(BASE_DIR / ".env")

COOKIES = {
    "bilibili": os.getenv("BILIBILI_COOKIE", ""),
    "xiaohongshu": os.getenv("XIAOHONGSHU_COOKIE", ""),
    "douyin": os.getenv("DOUYIN_COOKIE", ""),
    "xianyu": os.getenv("XIANYU_COOKIE", ""),
    "1688": os.getenv("1688_COOKIE", ""),
    "pinduoduo": os.getenv("PINDUODUO_COOKIE", ""),
}

MIMO_CONFIG = {
    "api_key": os.getenv("MIMO_API_KEY", ""),
    "base_url": os.getenv("MIMO_BASE_URL", "https://token-plan-cn.xiaomimimo.com/v1"),
    "model": os.getenv("MIMO_MODEL", "mimo-v2.5-pro"),
}

DATA_DIR = BASE_DIR / "data"
MEMORY_DIR = ROOT_DIR / "memory"
OUTPUTS_DIR = ROOT_DIR / "outputs"

DATA_DIR.mkdir(parents=True, exist_ok=True)
MEMORY_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive"
}

TIMEOUT = 30
RETRY_TIMES = 3
DELAY_BETWEEN_REQUESTS = 2

SCHEDULE_CONFIG = {
    "social_media": "06:00",
    "ecommerce": "05:00",
    "analysis": "08:00"
}

PLATFORM_CONFIG = {
    "bilibili": {
        "hot_url": "https://api.bilibili.com/x/web-interface/popular",
        "user_video_url": "https://api.bilibili.com/x/space/wbi/arc/search"
    },
    "douyin": {
        "hot_url": "https://www.douyin.com/aweme/v1/web/hot/search/list/",
        "user_video_url": ""
    },
    "xiaohongshu": {
        "hot_url": "https://edith.xiaohongshu.com/api/sns/web/v1/homefeed",
        "note_url": "https://edith.xiaohongshu.com/api/sns/web/v1/feed"
    },
    "1688": {
        "search_url": "https://s.1688.com/selloffer/offer_search.htm"
    },
    "pinduoduo": {
        "search_url": "https://search.pinduoduo.com/api/search"
    },
    "xianyu": {
        "search_url": "https://s2.goofish.com/router"
    }
}

PROFIT_CONFIG = {
    "platform_fee_rate": 0.06,
    "shipping_cost": 8,
    "min_profit_margin": 20,
    "target_profit_rate": 0.3
}

ANALYSIS_CONFIG = {
    "top_keywords_count": 20,
    "hot_title_threshold": 10000,
    "content_summary_length": 500
}
