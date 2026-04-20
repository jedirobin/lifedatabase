#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from crawlers.bilibili_crawler import BilibiliScraper
from storages.obsidian_writer import ObsidianSyncer

print("="*70)
print("开始全链路测试")
print("="*70)

try:
    print("\n【1/4】初始化爬虫...")
    scraper = BilibiliScraper()
    
    print("\n【2/4】抓取数据（含评论弹幕）...")
    data = scraper.get_hot_content(limit=2)
    print(f"   成功抓取 {len(data)} 条")
    
    for i, item in enumerate(data):
        print(f"\n   视频 {i+1}:")
        print(f"      - 标题: {item.get('title', '')[:30]}...")
        print(f"      - 评论数: {len(item.get('comments', []))}")
        print(f"      - 弹幕数: {len(item.get('danmaku', []))}")
    
    print("\n【3/4】保存数据（标准化格式）...")
    save_path = scraper.save_data()
    print(f"   保存路径: {save_path}")
    print(f"   文件大小: {save_path.stat().st_size} bytes")
    
    print("\n【4/4】同步到 Obsidian 并生成报告...")
    syncer = ObsidianSyncer()
    syncer.sync_data("bilibili", data, "test")
    print(f"   同步完成")
    
    print("\n" + "="*70)
    print("✅ 全链路测试通过！")
    print("="*70)

except Exception as e:
    print(f"\n❌ 错误: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
