#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能多平台爬虫 + 知识库系统
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from loguru import logger
import argparse


def print_banner():
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    
    print("=" * 60)
    print(r"""
   _____           _   _____ _       _
  / ____|         | | / ____| |     | |
 | |  __ _ __ __ _| || |    | |_   _| |__   ___
 | | |_ | '__/ _` | || |    | | | | | '_ \ / _ \
 | |__| | | | (_| | || |____| | |_| | |_) |  __/
  \_____|_|  \__,_|_| \_____|_|\__,_|_.__/ \___|

  GrabLab - 智能多平台爬虫 + 知识库系统 v1.0
    """)
    print("=" * 60)
    print()


def run_single_platform(platform: str, limit: int = 50, keyword: str = None):
    mode = "search" if keyword else "hot"
    logger.info(f"运行平台: {platform}, 模式: {mode}, 数量: {limit}")
    if keyword:
        logger.info(f"搜索关键词: {keyword}")
    
    if platform == "bilibili":
        from crawlers.bilibili_crawler import BilibiliScraper
        from analyzers.content_analyzer import HotContentAnalyzer
        
        scraper = BilibiliScraper()
        data = scraper.run(mode=mode, limit=limit, sync=True, keyword=keyword)
        
        if data:
            analyzer = HotContentAnalyzer()
            analyzer.save_analysis(f"bilibili_{keyword}" if keyword else "bilibili", data)
    
    elif platform == "xiaohongshu":
        from crawlers.xiaohongshu_crawler import XiaohongshuScraper
        from analyzers.content_analyzer import HotContentAnalyzer
        
        scraper = XiaohongshuScraper()
        data = scraper.run(mode=mode, limit=limit, sync=True, keyword=keyword)
        
        if data:
            analyzer = HotContentAnalyzer()
            analyzer.save_analysis(f"xiaohongshu_{keyword}" if keyword else "xiaohongshu", data)
    
    elif platform == "douyin":
        from crawlers.douyin_crawler import DouyinScraper
        from analyzers.content_analyzer import HotContentAnalyzer
        
        scraper = DouyinScraper()
        data = scraper.run(mode=mode, limit=limit, sync=True, keyword=keyword)
        
        if data:
            analyzer = HotContentAnalyzer()
            analyzer.save_analysis(f"douyin_{keyword}" if keyword else "douyin", data)
    
    elif platform == "ecommerce":
        from scheduler.task_scheduler import TaskScheduler
        scheduler = TaskScheduler()
        scheduler.task_ecommerce_selection()
    
    else:
        logger.error(f"未知平台: {platform}")


def run_all(limit: int = 50):
    logger.info("执行完整的爬虫+分析流程")
    
    for platform in ["bilibili", "xiaohongshu", "douyin", "ecommerce"]:
        run_single_platform(platform, limit)
    
    from scheduler.task_scheduler import TaskScheduler
    scheduler = TaskScheduler()
    scheduler.task_git_sync()
    
    logger.success("✅ 所有任务执行完成！")


def run_scheduler():
    from scheduler.task_scheduler import TaskScheduler
    scheduler = TaskScheduler()
    scheduler.start()


def run_webui():
    from webui import run_webui as webui
    webui()


def run_dream_cycle():
    from dream_cycle import DreamCycle
    dream_cycle = DreamCycle()
    dream_cycle.run_dream_cycle()


def run_dream_scheduler():
    from dream_cycle import DreamCycle
    dream_cycle = DreamCycle()
    dream_cycle.start()


def run_mimo_test():
    from mimo_client import test_connection
    test_connection()


def main():
    parser = argparse.ArgumentParser(description="🚀 智能多平台爬虫系统")
    parser.add_argument("-p", "--platform", 
                       choices=["bilibili", "xiaohongshu", "douyin", "ecommerce", "all"],
                       default="all",
                       help="选择要爬取的平台")
    parser.add_argument("-l", "--limit", type=int, default=50,
                       help="抓取数量")
    parser.add_argument("-k", "--keyword", type=str,
                       help="指定关键词/主题搜索抓取")
    parser.add_argument("-s", "--scheduler", action="store_true",
                       help="启动定时任务调度器")
    parser.add_argument("-o", "--once", action="store_true",
                       help="执行一次完整任务并退出")
    parser.add_argument("-w", "--web", action="store_true",
                       help="启动Web前端界面")
    parser.add_argument("-d", "--dream", action="store_true",
                       help="执行一次梦境循环")
    parser.add_argument("-ds", "--dream-scheduler", action="store_true",
                       help="启动梦境循环定时任务")
    parser.add_argument("-m", "--mimo", action="store_true",
                       help="测试MiMo大模型连接")
    
    args = parser.parse_args()
    
    print_banner()
    
    if args.scheduler:
        run_scheduler()
    elif args.once:
        run_all(args.limit)
    elif args.web:
        run_webui()
    elif args.dream:
        run_dream_cycle()
    elif args.dream_scheduler:
        run_dream_scheduler()
    elif args.mimo:
        run_mimo_test()
    else:
        run_single_platform(args.platform, args.limit, args.keyword)


if __name__ == "__main__":
    main()
