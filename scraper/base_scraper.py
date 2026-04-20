import time
import random
import json
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from loguru import logger
from fake_useragent import UserAgent

from config import HEADERS, TIMEOUT, RETRY_TIMES, DELAY_BETWEEN_REQUESTS, DATA_DIR


class BaseScraper(ABC):
    def __init__(self, platform_name: str):
        self.platform_name = platform_name
        self.ua = UserAgent()
        self.session = requests.Session()
        self.data = []
        self.setup_logger()
    
    def setup_logger(self):
        self.logger = logger
        self.logger.add(
            DATA_DIR / f"{self.platform_name}_scraper.log",
            rotation="10 MB",
            retention="7 days",
            encoding="utf-8"
        )
    
    def get_headers(self) -> Dict[str, str]:
        headers = HEADERS.copy()
        headers["User-Agent"] = self.ua.random
        return headers
    
    def request(self, url: str, method: str = "GET", **kwargs) -> Optional[requests.Response]:
        for attempt in range(RETRY_TIMES):
            try:
                delay = DELAY_BETWEEN_REQUESTS + random.uniform(0, 2)
                time.sleep(delay)
                
                kwargs.setdefault("headers", self.get_headers())
                kwargs.setdefault("timeout", TIMEOUT)
                
                response = self.session.request(method, url, **kwargs)
                response.raise_for_status()
                return response
                
            except Exception as e:
                logger.warning(f"请求失败 (尝试 {attempt + 1}/{RETRY_TIMES}): {url}, 错误: {e}")
                if attempt == RETRY_TIMES - 1:
                    logger.error(f"请求最终失败: {url}")
                    return None
    
    def request_json(self, url: str, **kwargs) -> Optional[Dict[str, Any]]:
        response = self.request(url, **kwargs)
        if response:
            try:
                return response.json()
            except json.JSONDecodeError as e:
                logger.error(f"JSON解析失败: {e}")
        return None
    
    def request_soup(self, url: str, **kwargs) -> Optional[BeautifulSoup]:
        response = self.request(url, **kwargs)
        if response:
            return BeautifulSoup(response.text, "html.parser")
        return None
    
    @abstractmethod
    def get_hot_content(self, limit: int = 50) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def get_user_content(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def search_content(self, keyword: str, limit: int = 50) -> List[Dict[str, Any]]:
        pass
    
    def save_data(self, filename: str = None) -> Path:
        if not filename:
            filename = f"{self.platform_name}_{time.strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = DATA_DIR / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"数据已保存: {filepath}")
        return filepath
    
    def sync_to_obsidian(self, data_type: str = "hot"):
        from obsidian_sync import ObsidianSyncer
        syncer = ObsidianSyncer()
        syncer.sync_data(self.platform_name, self.data, data_type)
    
    def run(self, mode: str = "hot", limit: int = 50, sync: bool = True, keyword: str = None):
        self.logger.info(f"开始 {self.platform_name} 爬虫, 模式: {mode}, 数量: {limit}")
        
        if mode == "hot":
            self.data = self.get_hot_content(limit)
        elif mode == "user":
            user_id = input("请输入用户ID: ")
            self.data = self.get_user_content(user_id, limit)
        elif mode == "search" and keyword:
            self.data = self.search_content(keyword, limit)
        
        self.logger.info(f"抓取完成, 共获取 {len(self.data)} 条数据")
        
        self.save_data()
        if sync:
            sync_type = keyword if keyword else mode
            self.sync_to_obsidian(sync_type)
        
        return self.data
