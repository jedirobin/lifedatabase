#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
登录会话管理器
"""
import json
from pathlib import Path
from loguru import logger
from config import COOKIES


class LoginManager:
    """统一登录管理器"""
    
    def __init__(self, platform: str):
        self.platform = platform
        self.cookie = COOKIES.get(platform, "")
        self.session_expire = None
    
    def is_logged_in(self):
        """检查是否已登录"""
        return bool(self.cookie and len(self.cookie) > 10)
    
    def get_cookie(self):
        """获取当前Cookie"""
        return self.cookie
    
    def set_cookie(self, cookie_str: str):
        """手动设置Cookie"""
        self.cookie = cookie_str
        logger.info(f"{self.platform} Cookie已更新")
    
    def save_session(self, filepath: str = None):
        """保存会话到本地"""
        if not filepath:
            filepath = f".sessions/{self.platform}_session.json"
        
        Path(filepath).parent.mkdir(exist_ok=True)
        
        session_data = {
            "platform": self.platform,
            "cookie": self.cookie,
            "saved_at": __import__("time").time()
        }
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(session_data, f, ensure_ascii=False)
        
        logger.info(f"会话已保存: {filepath}")
    
    def load_session(self, filepath: str = None):
        """从本地加载会话"""
        if not filepath:
            filepath = f".sessions/{self.platform}_session.json"
        
        if Path(filepath).exists():
            with open(filepath, "r", encoding="utf-8") as f:
                session_data = json.load(f)
                self.cookie = session_data.get("cookie", "")
                logger.info(f"已加载{self.platform}会话")
                return True
        return False
    
    def get_headers(self):
        """生成请求头"""
        return {
            "Cookie": self.cookie,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
