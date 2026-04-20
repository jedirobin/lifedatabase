import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

import pandas as pd
from loguru import logger


class ObsidianSyncer:
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.memory_dir = self.root_dir / "memory"
        self.insights_dir = self.memory_dir / "insights"
        self.reports_dir = self.root_dir / "outputs" / "reports"
        self.index_file = self.memory_dir / "index.md"
    
    def _flatten_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        flattened = []
        for item in data:
            flat = {}
            flat["title"] = item.get("video_info", {}).get("title", "") or item.get("title", "")
            flat["url"] = item.get("video_info", {}).get("video_url", "") or item.get("url", "")
            
            author = item.get("author", {})
            if isinstance(author, dict):
                flat["author"] = author.get("name", "")
            else:
                flat["author"] = str(author)
            
            stats = item.get("stats", {})
            if isinstance(stats, dict):
                flat["play_count"] = stats.get("view_count", 0) or item.get("play_count", 0)
                flat["like_count"] = stats.get("like_count", 0) or item.get("like_count", 0)
            else:
                flat["play_count"] = item.get("play_count", 0)
                flat["like_count"] = item.get("like_count", 0)
            
            flat["publish_time"] = item.get("publish_time", "")
            flat["tags"] = item.get("video_info", {}).get("tags", []) or item.get("tags", [])
            
            flattened.append(flat)
        return flattened
    
    def generate_hot_report(self, platform: str, data: List[Dict[str, Any]]) -> str:
        flat_data = self._flatten_data(data)
        df = pd.DataFrame(flat_data)
        
        if df.empty:
            total_play = 0
            avg_play = 0
            top10 = pd.DataFrame()
        else:
            if "play_count" in df.columns:
                total_play = df["play_count"].sum()
                avg_play = df["play_count"].mean()
                top10 = df.nlargest(10, "play_count")
            else:
                total_play = 0
                avg_play = 0
                top10 = df.head(10)
        
        report_content = f"""---
title: {platform}爆款内容分析报告
type: report
platform: {platform}
generated: {datetime.now().strftime('%Y-%m-%d')}
tags: ["数据分析", "爆款分析", "{platform}"]
---

# {platform}爆款内容分析报告

> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 数据概览

| 指标 | 数值 |
|------|------|
| 样本数量 | {len(df)} 条 |
| 总播放/曝光量 | {total_play:,} |
| 平均播放量 | {avg_play:,.0f} |

## 🔥 Top 10 爆款内容

"""
        
        if not top10.empty:
            for _, row in top10.iterrows():
                report_content += f"""
### [{row.get('title', '无标题')}]({row.get('url', '#')})

- **作者**: {row.get('author', '未知')}
- **播放/点赞**: {row.get('play_count', 0):,} / {row.get('like_count', 0):,}
- **发布时间**: {row.get('publish_time', '未知')}
- **核心标签**: {', '.join(row.get('tags', []))}

"""
        
        report_content += """
## 💡 爆款洞察

请结合具体数据进一步分析爆款规律...

---

*本报告由爬虫系统自动生成*
"""
        return report_content
    
    def generate_product_report(self, platform: str, data: List[Dict[str, Any]]) -> str:
        df = pd.DataFrame(data)
        
        if df.empty:
            high_profit = pd.DataFrame()
        elif "profit" in df.columns:
            high_profit = df[df["profit"] > 20].sort_values("profit", ascending=False)
        else:
            high_profit = df.head(20)
        
        report_content = f"""---
title: {platform}选品分析报告
type: report
platform: {platform}
generated: {datetime.now().strftime('%Y-%m-%d')}
tags: ["选品", "电商", "{platform}"]
---

# {platform}选品分析报告

> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 选品概览

| 指标 | 数值 |
|------|------|
| 商品数量 | {len(df)} 个 |
| 高利润商品数 | {len(high_profit)} 个 |

## 💰 推荐选品清单

| 商品名称 | 平台售价 | 进货价 | 预估利润 | 利润率 |
|----------|----------|--------|----------|--------|
"""
        
        if not high_profit.empty:
            for _, row in high_profit.head(15).iterrows():
                price = row.get('price', 0)
                cost = row.get('cost_price', price * 0.5)
                profit = row.get('profit', price - cost - 8)
                profit_rate = (profit / price * 100) if price > 0 else 0
                
                report_content += f"| {row.get('title', '未知')[:30]} | ¥{price:.2f} | ¥{cost:.2f} | **¥{profit:.2f}** | {profit_rate:.1f}% |\n"
        
        report_content += """
## 📝 选品建议

请结合利润空间、竞争程度、供应链稳定性综合评估...

---

*本报告由爬虫系统自动生成*
"""
        return report_content
    
    def sync_data(self, platform: str, data: List[Dict[str, Any]], data_type: str = "hot"):
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        e_commerce_platforms = ["xianyu", "1688", "pinduoduo", "taobao"]
        
        if platform in e_commerce_platforms:
            report_content = self.generate_product_report(platform, data)
            filename = f"{platform}_选品分析_{datetime.now().strftime('%Y%m%d')}.md"
        else:
            report_content = self.generate_hot_report(platform, data)
            filename = f"{platform}_内容分析_{datetime.now().strftime('%Y%m%d')}.md"
        
        filepath = self.reports_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(report_content)
        
        logger.success(f"已生成分析报告: {filepath}")
        
        raw_dir = self.root_dir / "sources" / platform
        raw_dir.mkdir(parents=True, exist_ok=True)
        
        raw_file = raw_dir / f"{platform}_raw_{int(time.time())}.json"
        with open(raw_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.success(f"原始数据已存档: {raw_file}")
