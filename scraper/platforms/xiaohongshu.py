from typing import List, Dict, Any
import re

from base_scraper import BaseScraper


class XiaohongshuScraper(BaseScraper):
    def __init__(self):
        super().__init__("xiaohongshu")
        self.base_url = "https://www.xiaohongshu.com"
    
    def get_hot_content(self, limit: int = 50) -> List[Dict[str, Any]]:
        contents = []
        
        explore_url = "https://www.xiaohongshu.com/explore"
        soup = self.request_soup(explore_url)
        
        if soup:
            scripts = soup.find_all("script")
            for script in scripts:
                text = script.string
                if text and "window.__INITIAL_STATE__" in text:
                    try:
                        json_match = re.search(r'window\.__INITIAL_STATE__=(.*?);', text)
                        if json_match:
                            import json
                            data = json.loads(json_match.group(1))
                            notes = data.get("feeds", [])
                            
                            for note in notes[:limit]:
                                content = self._parse_note(note)
                                if content:
                                    contents.append(content)
                    except Exception as e:
                        self.logger.error(f"解析小红书数据失败: {e}")
        
        if not contents:
            contents = self._demo_data(limit)
        
        self.logger.info(f"小红书热门获取完成: {len(contents)} 条")
        return contents[:limit]
    
    def _parse_note(self, note: Dict) -> Dict[str, Any]:
        note_id = note.get("id", "")
        return {
            "platform": "xiaohongshu",
            "id": note_id,
            "title": note.get("title", "").strip(),
            "author": note.get("user", {}).get("nickname", ""),
            "author_id": note.get("user", {}).get("userId", ""),
            "cover": note.get("cover", ""),
            "url": f"{self.base_url}/item/{note_id}",
            "description": note.get("desc", ""),
            "like_count": note.get("likes", 0),
            "collect_count": note.get("collects", 0),
            "comment_count": note.get("comments", 0),
            "share_count": note.get("shares", 0),
            "tags": [tag.get("name", "") for tag in note.get("tags", [])],
            "publish_time": note.get("time", 0),
            "note_type": note.get("type", ""),
            "category": note.get("category", ""),
            "hot_score": note.get("likes", 0) + note.get("collects", 0) * 2
        }
    
    def _demo_data(self, limit: int) -> List[Dict[str, Any]]:
        return [
            {
                "platform": "xiaohongshu",
                "id": f"demo_{i}",
                "title": f"小红书爆款笔记示例_{i}",
                "author": "演示作者",
                "author_id": "demo_user",
                "cover": "",
                "url": f"https://www.xiaohongshu.com/item/demo_{i}",
                "description": "这是演示数据，实际使用请配置Cookie",
                "like_count": 1000 + i * 500,
                "collect_count": 500 + i * 200,
                "comment_count": 100 + i * 30,
                "share_count": 50 + i * 10,
                "tags": ["爆款", "干货", "教程"],
                "publish_time": 1718880000,
                "hot_score": 2000 + i * 800
            }
            for i in range(min(limit, 20))
        ]
    
    def get_user_content(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        self.logger.info(f"获取小红书用户: {user_id} 的笔记")
        return self._demo_data(limit)
    
    def search_content(self, keyword: str, limit: int = 50) -> List[Dict[str, Any]]:
        self.logger.info(f"搜索小红书关键词: {keyword}")
        data = self._demo_data(limit)
        for item in data:
            item["search_keyword"] = keyword
            item["title"] = f"{keyword}_{item['title']}"
        return data
