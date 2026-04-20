#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from crawlers.bilibili_crawler import BilibiliScraper

print("="*60)
print("开始调试 B站爬虫")
print("="*60)

scraper = BilibiliScraper()

try:
    print("\n1. 测试获取热门...")
    data = scraper.get_hot_content(limit=3)
    print(f"   抓取到: {len(data)} 条")
    
    for i, d in enumerate(data):
        print(f"\n视频 {i+1}:")
        print(f"  标题: {d.get('title', '')[:30]}...")
        print(f"  评论数: {len(d.get('comments', []))}")
        print(f"  弹幕数: {len(d.get('danmaku', []))}")

    print("\n2. 测试保存数据...")
    path = scraper.save_data()
    print(f"   保存到: {path}")
    print(f"   文件存在: {path.exists()}")

    print("\n3. 测试同步...")
    scraper.sync_to_obsidian("test")
    print("   同步完成!")

    print("\n" + "="*60)
    print("✅ 所有测试通过!")
    print("="*60)

except Exception as e:
    print(f"\n❌ 错误: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
