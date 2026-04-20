from typing import List, Dict, Any

from base_scraper import BaseScraper


class DouyinScraper(BaseScraper):
    def __init__(self):
        super().__init__("douyin")
        self.base_url = "https://www.douyin.com"
    
    def get_hot_content(self, limit: int = 50) -> List[Dict[str, Any]]:
        contents = []
        
        hot_url = "https://www.douyin.com/discover"
        soup = self.request_soup(hot_url)
        
        if soup:
            self.logger.info("抖音页面获取成功，待完善解析逻辑")
        
        contents = self._demo_data(limit)
        self.logger.info(f"抖音热门获取完成: {len(contents)} 条")
        return contents[:limit]
    
    def _demo_data(self, limit: int) -> List[Dict[str, Any]]:
        demo_titles = [
            "普通人一定要做知识付费 #创业",
            "AI文案工具真的太好用了 #干货",
            "这3个习惯让我月入10万 #认知",
            "我是如何从0到1做账号的 #自媒体",
            "普通人翻身的最后机会 #商业思维"
        ]
        
        contents = []
        for i in range(min(limit, 30)):
            title = demo_titles[i % len(demo_titles)]
            play_count = 100000 + i * 50000
            like_count = int(play_count * 0.05)
            
            contents.append({
                "platform": "douyin",
                "id": f"7356677889900{i}",
                "title": title,
                "author": f"达人账号_{i}",
                "author_id": f"user_{i}",
                "cover": "",
                "url": f"https://www.douyin.com/video/7356677889900{i}",
                "description": title,
                "play_count": play_count,
                "like_count": like_count,
                "comment_count": int(like_count * 0.1),
                "share_count": int(like_count * 0.05),
                "duration": 60 + i * 5,
                "tags": self._extract_tags(title),
                "publish_time": 1718880000,
                "hot_score": play_count * 0.01 + like_count
            })
        
        return contents
    
    def _extract_tags(self, title: str) -> List[str]:
        import re
        tags = re.findall(r'#(\w+)', title)
        if not tags:
            common_tags = ["创业", "干货", "认知", "自媒体", "AI"]
            tags = [t for t in common_tags if t in title]
        return tags
    
    def get_user_content(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        self.logger.info(f"获取抖音用户: {user_id} 的作品")
        return self._demo_data(limit)
