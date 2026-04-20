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


def run_single_platform(platform: str, limit: int = 50):
    logger.info(f"运行平台: {platform}, 数量: {limit}")
    
    if platform == "bilibili":
        from platforms.bilibili import BilibiliScraper
        from analyzers.content_analyzer import HotContentAnalyzer
        
        scraper = BilibiliScraper()
        data = scraper.run(limit=limit, sync=True)
        
        if data:
            analyzer = HotContentAnalyzer()
            analyzer.save_analysis("bilibili", data)
    
    elif platform == "xiaohongshu":
        from platforms.xiaohongshu import XiaohongshuScraper
        from analyzers.content_analyzer import HotContentAnalyzer
        
        scraper = XiaohongshuScraper()
        data = scraper.run(limit=limit, sync=True)
        
        if data:
            analyzer = HotContentAnalyzer()
            analyzer.save_analysis("xiaohongshu", data)
    
    elif platform == "douyin":
        from platforms.douyin import DouyinScraper
        from analyzers.content_analyzer import HotContentAnalyzer
        
        scraper = DouyinScraper()
        data = scraper.run(limit=limit, sync=True)
        
        if data:
            analyzer = HotContentAnalyzer()
            analyzer.save_analysis("douyin", data)
    
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


def main():
    parser = argparse.ArgumentParser(description="🚀 智能多平台爬虫系统")
    parser.add_argument("-p", "--platform", 
                       choices=["bilibili", "xiaohongshu", "douyin", "ecommerce", "all"],
                       default="all",
                       help="选择要爬取的平台")
    parser.add_argument("-l", "--limit", type=int, default=50,
                       help="抓取数量")
    parser.add_argument("-s", "--scheduler", action="store_true",
                       help="启动定时任务调度器")
    parser.add_argument("-o", "--once", action="store_true",
                       help="执行一次完整任务并退出")
    
    args = parser.parse_args()
    
    print_banner()
    
    if args.scheduler:
        run_scheduler()
    elif args.once:
        run_all(args.limit)
    else:
        run_single_platform(args.platform, args.limit)


if __name__ == "__main__":
    main()
