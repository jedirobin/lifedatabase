#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
反爬策略处理器
"""
import time
import random
from loguru import logger


class AntiCrawlerHandler:
    """反爬策略处理器"""
    
    def __init__(self):
        self.delay_range = (2.0, 5.0)
        self.request_count = 0
        self.last_request_time = 0
    
    def smart_delay(self):
        """智能随机延迟，模拟人类浏览行为"""
        delay = random.uniform(*self.delay_range)
        time.sleep(delay)
        self.last_request_time = time.time()
        self.request_count += 1
    
    def get_random_ua(self):
        """获取随机User-Agent"""
        ua_list = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36"
        ]
        return random.choice(ua_list)
    
    def human_like_mouse_path(self, start_x, start_y, end_x, end_y):
        """贝塞尔曲线模拟鼠标移动轨迹"""
        points = []
        steps = random.randint(20, 50)
        for i in range(steps):
            t = i / steps
            x = start_x + (end_x - start_x) * t + random.randint(-5, 5)
            y = start_y + (end_y - start_y) * t + random.randint(-3, 3)
            points.append((x, y))
        return points
    
    def should_rotate_cookie(self):
        """判断是否需要轮换Cookie"""
        return self.request_count > 0 and self.request_count % 100 == 0
    
    def handle_412_precondition(self):
        """处理412反爬拦截"""
        logger.warning("检测到412拦截，冷却30秒...")
        time.sleep(30)
        logger.info("冷却结束，继续抓取")
