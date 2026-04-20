from typing import List, Dict, Any

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from crawlers.base_crawler import BaseScraper
from config import PLATOFRM_CONFIG


class BilibiliScraper(BaseScraper):
    def __init__(self):
        super().__init__("bilibili")
        self.api_url = PLATOFRM_CONFIG["bilibili"]["hot_url"]
        self.fetch_comments = True
        self.fetch_danmaku = True
        self.max_comments_per_video = 100
    
    def get_video_comments(self, aid: str, bvid: str, limit: int = 100) -> List[Dict[str, Any]]:
        comments = []
        page = 1
        
        try:
            while len(comments) < limit:
                api_url = "https://api.bilibili.com/x/v2/reply"
                params = {
                    "type": 1,
                    "oid": aid,
                    "pn": page,
                    "ps": 20,
                    "sort": 2
                }
                
                result = self.request_json(api_url, params=params)
                
                if not result or result.get("code") != 0:
                    break
                
                replies = result.get("data", {}).get("replies", [])
                if not replies:
                    break
                
                for reply in replies:
                    comment = {
                        "comment_id": str(reply.get("rpid", "")),
                        "content": reply.get("content", {}).get("message", ""),
                        "author": reply.get("member", {}).get("uname", ""),
                        "author_id": str(reply.get("member", {}).get("mid", "")),
                        "like_count": reply.get("like", 0),
                        "reply_count": reply.get("rcount", 0),
                        "publish_time": reply.get("ctime", 0),
                        "floor": reply.get("floor", 0)
                    }
                    comments.append(comment)
                    
                    if len(comments) >= limit:
                        break
                
                page += 1
                if len(replies) < 20 or page > 5:
                    break
        
        except Exception as e:
            self.logger.debug(f"获取评论失败: {e}")
        
        return comments
    
    def get_video_danmaku(self, cid: str) -> List[Dict[str, Any]]:
        danmaku_list = []
        
        try:
            api_url = f"https://comment.bilibili.com/{cid}.xml"
            response = self.request(api_url)
            
            if not response:
                return danmaku_list
            
            import re
            pattern = r'<d p="([^"]+)">([^<]+)</d>'
            matches = re.findall(pattern, response.text)
            
            for match in matches[:500]:
                attrs = match[0].split(',')
                text = match[1]
                
                if len(attrs) >= 7:
                    danmaku = {
                        "time": float(attrs[0]),
                        "type": int(attrs[1]),
                        "font_size": int(attrs[2]),
                        "color": attrs[3],
                        "publish_time": int(attrs[4]),
                        "pool": int(attrs[5]),
                        "sender_id": attrs[6],
                        "content": text
                    }
                    danmaku_list.append(danmaku)
        
        except Exception as e:
            self.logger.debug(f"获取弹幕失败: {e}")
        
        return danmaku_list
    
    def get_video_detail(self, aid: str, bvid: str) -> Dict[str, Any]:
        detail = {
            "comments": [],
            "danmaku": []
        }
        
        try:
            api_url = "https://api.bilibili.com/x/web-interface/view"
            params = {"bvid": bvid}
            result = self.request_json(api_url, params=params)
            
            if result and result.get("code") == 0:
                cid = result.get("data", {}).get("cid", "")
                
                if self.fetch_comments:
                    detail["comments"] = self.get_video_comments(aid, bvid, self.max_comments_per_video)
                
                if self.fetch_danmaku and cid:
                    detail["danmaku"] = self.get_video_danmaku(cid)
        
        except Exception as e:
            self.logger.debug(f"获取详情失败: {e}")
        
        return detail
    
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
                aid = str(item.get("aid", ""))
                bvid = item.get("bvid", "")
                
                detail = self.get_video_detail(aid, bvid)
                
                content = {
                    "platform": "bilibili",
                    "id": aid,
                    "bvid": bvid,
                    "title": item.get("title", "").strip(),
                    "author": item.get("owner", {}).get("name", ""),
                    "author_id": str(item.get("owner", {}).get("mid", "")),
                    "cover": item.get("pic", ""),
                    "url": f"https://www.bilibili.com/video/{bvid}",
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
                    "hot_score": stat.get("view", 0) * 0.1 + stat.get("like", 0) * 2,
                    "comments": detail["comments"],
                    "danmaku": detail["danmaku"]
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
                aid = str(item.get("aid", ""))
                bvid = item.get("bvid", "")
                
                detail = self.get_video_detail(aid, bvid)
                
                content = {
                    "platform": "bilibili",
                    "search_keyword": keyword,
                    "id": aid,
                    "bvid": bvid,
                    "title": item.get("title", "").strip().replace('<em class="keyword">', '').replace('</em>', ''),
                    "author": item.get("author", ""),
                    "author_id": str(item.get("mid", "")),
                    "cover": item.get("pic", ""),
                    "url": f"https://www.bilibili.com/video/{bvid}",
                    "description": item.get("description", ""),
                    "play_count": item.get("play", 0),
                    "like_count": 0,
                    "comment_count": item.get("review", 0),
                    "duration": item.get("duration", ""),
                    "tags": [keyword],
                    "publish_time": item.get("pubdate", 0),
                    "hot_score": item.get("play", 0),
                    "comments": detail["comments"],
                    "danmaku": detail["danmaku"]
                }
                contents.append(content)
            
            page += 1
            if len(items) < page_size:
                break
        
        self.logger.info(f"搜索 '{keyword}' 完成，共获取 {len(contents)} 条结果")
        return contents[:limit]
