from typing import List, Dict, Any

from base_scraper import BaseScraper
from config import PLATOFRM_CONFIG


class BilibiliScraper(BaseScraper):
    def __init__(self):
        super().__init__("bilibili")
        self.api_url = PLATOFRM_CONFIG["bilibili"]["hot_url"]
    
    def get_hot_content(self, limit: int = 50) -> List[Dict[str, Any]]:
        contents = []
        page = 1
        page_size = 20
        
        while len(contents) < limit:
            params = {
                "pn": page,
                "ps": min(page_size, limit - len(contents))
            }
            
            result = self.request_json(self.api_url, params=params)
            
            if not result or result.get("code") != 0:
                self.logger.error(f"获取热门数据失败: {result}")
                break
            
            items = result.get("data", {}).get("list", [])
            if not items:
                break
            
            for item in items:
                stat = item.get("stat", {})
                content = {
                    "platform": "bilibili",
                    "id": str(item.get("aid", "")),
                    "bvid": item.get("bvid", ""),
                    "title": item.get("title", "").strip(),
                    "author": item.get("owner", {}).get("name", ""),
                    "author_id": str(item.get("owner", {}).get("mid", "")),
                    "cover": item.get("pic", ""),
                    "url": f"https://www.bilibili.com/video/{item.get('bvid', '')}",
                    "description": item.get("desc", ""),
                    "play_count": stat.get("view", 0),
                    "like_count": stat.get("like", 0),
                    "comment_count": stat.get("reply", 0),
                    "coin_count": stat.get("coin", 0),
                    "collect_count": stat.get("favorite", 0),
                    "share_count": stat.get("share", 0),
                    "danmaku_count": stat.get("danmaku", 0),
                    "duration": item.get("duration", 0),
                    "tags": [item.get("tname", "")],
                    "publish_time": item.get("pubdate", 0),
                    "category": item.get("tname", ""),
                    "hot_score": stat.get("view", 0) * 0.1 + stat.get("like", 0) * 2
                }
                contents.append(content)
            
            page += 1
            if len(items) < page_size:
                break
        
        self.logger.info(f"B站热门获取完成: {len(contents)} 条")
        return contents[:limit]
    
    def get_user_content(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        contents = []
        
        api_url = f"https://api.bilibili.com/x/space/wbi/arc/search"
        params = {
            "mid": user_id,
            "ps": min(limit, 50),
            "pn": 1,
            "order": "pubdate"
        }
        
        result = self.request_json(api_url, params=params)
        
        if result and result.get("code") == 0:
            items = result.get("data", {}).get("list", {}).get("vlist", [])
            for item in items[:limit]:
                content = {
                    "platform": "bilibili",
                    "id": str(item.get("aid", "")),
                    "bvid": item.get("bvid", ""),
                    "title": item.get("title", "").strip(),
                    "author": item.get("author", ""),
                    "author_id": user_id,
                    "cover": item.get("pic", ""),
                    "url": f"https://www.bilibili.com/video/{item.get('bvid', '')}",
                    "description": item.get("description", ""),
                    "play_count": item.get("play", 0),
                    "like_count": 0,
                    "comment_count": item.get("comment", 0),
                    "duration": item.get("length", ""),
                    "tags": [],
                    "publish_time": item.get("created", 0)
                }
                contents.append(content)
        
        self.logger.info(f"用户 {user_id} 视频获取完成: {len(contents)} 条")
        return contents
    
    def search_content(self, keyword: str, limit: int = 50) -> List[Dict[str, Any]]:
        contents = []
        page = 1
        page_size = 20
        
        self.logger.info(f"搜索关键词: {keyword}")
        
        while len(contents) < limit:
            api_url = "https://api.bilibili.com/x/web-interface/search/type"
            params = {
                "search_type": "video",
                "keyword": keyword,
                "page": page,
                "pagesize": min(page_size, limit - len(contents)),
                "order": "click"
            }
            
            result = self.request_json(api_url, params=params)
            
            if not result or result.get("code") != 0:
                break
            
            items = result.get("data", {}).get("result", [])
            if not items:
                break
            
            for item in items:
                content = {
                    "platform": "bilibili",
                    "search_keyword": keyword,
                    "id": str(item.get("aid", "")),
                    "bvid": item.get("bvid", ""),
                    "title": item.get("title", "").strip().replace('<em class="keyword">', '').replace('</em>', ''),
                    "author": item.get("author", ""),
                    "author_id": str(item.get("mid", "")),
                    "cover": item.get("pic", ""),
                    "url": f"https://www.bilibili.com/video/{item.get('bvid', '')}",
                    "description": item.get("description", ""),
                    "play_count": item.get("play", 0),
                    "like_count": 0,
                    "comment_count": item.get("review", 0),
                    "duration": item.get("duration", ""),
                    "tags": [keyword],
                    "publish_time": item.get("pubdate", 0),
                    "hot_score": item.get("play", 0)
                }
                contents.append(content)
            
            page += 1
            if len(items) < page_size:
                break
        
        self.logger.info(f"搜索 '{keyword}' 完成，共获取 {len(contents)} 条结果")
        return contents[:limit]
