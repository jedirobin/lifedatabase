import time
import schedule
from datetime import datetime
from loguru import logger

from config import SCHEDULE_CONFIG


class TaskScheduler:
    def __init__(self):
        self.running = False
    
    def task_bilibili_hot(self):
        logger.info("=" * 50)
        logger.info("开始执行: B站热门数据抓取")
        
        from platforms.bilibili import BilibiliScraper
        from analyzers.content_analyzer import HotContentAnalyzer
        
        scraper = BilibiliScraper()
        data = scraper.run(limit=50, sync=True)
        
        if data:
            analyzer = HotContentAnalyzer()
            analyzer.save_analysis("bilibili", data)
        
        logger.info("B站任务完成")
    
    def task_xiaohongshu_hot(self):
        logger.info("=" * 50)
        logger.info("开始执行: 小红书热门数据抓取")
        
        from platforms.xiaohongshu import XiaohongshuScraper
        from analyzers.content_analyzer import HotContentAnalyzer
        
        scraper = XiaohongshuScraper()
        data = scraper.run(limit=50, sync=True)
        
        if data:
            analyzer = HotContentAnalyzer()
            analyzer.save_analysis("xiaohongshu", data)
        
        logger.info("小红书任务完成")
    
    def task_douyin_hot(self):
        logger.info("=" * 50)
        logger.info("开始执行: 抖音热门数据抓取")
        
        from platforms.douyin import DouyinScraper
        from analyzers.content_analyzer import HotContentAnalyzer
        
        scraper = DouyinScraper()
        data = scraper.run(limit=50, sync=True)
        
        if data:
            analyzer = HotContentAnalyzer()
            analyzer.save_analysis("douyin", data)
        
        logger.info("抖音任务完成")
    
    def task_ecommerce_selection(self):
        logger.info("=" * 50)
        logger.info("开始执行: 电商选品分析")
        
        from analyzers.product_analyzer import ProfitAnalyzer
        
        demo_products = self._demo_product_data()
        
        analyzer = ProfitAnalyzer()
        analyzer.save_report("电商综合", demo_products)
        
        logger.info("电商选品任务完成")
    
    def _demo_product_data(self):
        categories = ["数码配件", "家居用品", "美妆工具", "户外运动", "汽车用品"]
        products = []
        
        for i in range(50):
            price = round(30 + i * 5 + __import__('random').random() * 50, 2)
            cost = round(price * (0.3 + __import__('random').random() * 0.3), 2)
            
            products.append({
                "title": f"电商爆款商品_{i}",
                "price": price,
                "cost_price": cost,
                "category": categories[i % len(categories)],
                "sales": 100 + i * 50
            })
        
        return products
    
    def task_git_sync(self):
        logger.info("=" * 50)
        logger.info("开始执行: Git自动同步")
        
        import subprocess
        from pathlib import Path
        
        repo_dir = Path(__file__).parent.parent.parent
        
        try:
            subprocess.run(["git", "add", "."], cwd=repo_dir, capture_output=True)
            result = subprocess.run(
                ["git", "commit", "-m", f"auto: 爬虫数据更新 {datetime.now().strftime('%Y-%m-%d %H:%M')}"],
                cwd=repo_dir, capture_output=True, text=True
            )
            if "nothing to commit" not in result.stdout:
                subprocess.run(["git", "push"], cwd=repo_dir, capture_output=True)
                logger.info("Git同步完成")
            else:
                logger.info("无变更需要提交")
        except Exception as e:
            logger.error(f"Git同步失败: {e}")
    
    def setup_schedule(self):
        schedule.every().day.at("06:00").do(self.task_bilibili_hot)
        schedule.every().day.at("06:30").do(self.task_xiaohongshu_hot)
        schedule.every().day.at("07:00").do(self.task_douyin_hot)
        schedule.every().day.at("05:00").do(self.task_ecommerce_selection)
        
        schedule.every(6).hours.do(self.task_git_sync)
        
        logger.info("定时任务已设置:")
        for job in schedule.jobs:
            logger.info(f"  - {job}")
    
    def run_once(self):
        logger.info("执行一次完整爬虫任务...")
        self.task_bilibili_hot()
        self.task_xiaohongshu_hot()
        self.task_douyin_hot()
        self.task_ecommerce_selection()
        self.task_git_sync()
        logger.info("单次任务执行完成")
    
    def start(self):
        self.setup_schedule()
        self.running = True
        
        logger.info("定时任务调度器启动，按Ctrl+C停止")
        
        try:
            while self.running:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            logger.info("调度器已停止")
