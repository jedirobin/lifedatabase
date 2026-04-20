import json
from typing import List, Dict, Any, Tuple
from datetime import datetime
from pathlib import Path

import pandas as pd

from config import PROFIT_CONFIG, MEMORY_DIR


class ProfitAnalyzer:
    def __init__(self):
        self.platform_fee = PROFIT_CONFIG["platform_fee_rate"]
        self.shipping_cost = PROFIT_CONFIG["shipping_cost"]
        self.min_profit = PROFIT_CONFIG["min_profit_margin"]
        self.target_rate = PROFIT_CONFIG["target_profit_rate"]
        
        self.result_dir = MEMORY_DIR / "insights"
        self.result_dir.mkdir(exist_ok=True)
    
    def calculate_profit(self, 
                         sale_price: float, 
                         cost_price: float, 
                         shipping_fee: float = None) -> Dict[str, Any]:
        if shipping_fee is None:
            shipping_fee = self.shipping_cost
        
        service_fee = sale_price * self.platform_fee
        total_cost = cost_price + shipping_fee + service_fee
        net_profit = sale_price - total_cost
        profit_rate = (net_profit / sale_price * 100) if sale_price > 0 else 0
        
        return {
            "sale_price": round(sale_price, 2),
            "cost_price": round(cost_price, 2),
            "shipping_fee": round(shipping_fee, 2),
            "service_fee": round(service_fee, 2),
            "total_cost": round(total_cost, 2),
            "net_profit": round(net_profit, 2),
            "profit_rate": round(profit_rate, 2),
            "is_recommended": net_profit >= self.min_profit and profit_rate >= (self.target_rate * 100),
            "rating": self._get_profit_rating(net_profit, profit_rate)
        }
    
    def _get_profit_rating(self, profit: float, rate: float) -> str:
        if profit >= 50 and rate >= 50:
            return "S"
        elif profit >= 30 and rate >= 35:
            return "A"
        elif profit >= 20 and rate >= 25:
            return "B"
        elif profit >= 10:
            return "C"
        else:
            return "D"
    
    def analyze_products(self, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        for p in products:
            p["profit"] = self.calculate_profit(
                p.get("price", 0),
                p.get("cost_price", p.get("price", 0) * 0.5)
            )
        
        df = pd.DataFrame([{**p, **p.pop('profit')} for p in products])
        
        recommended = df[df["is_recommended"]].sort_values("net_profit", ascending=False)
        high_rated = df[df["rating"].isin(["S", "A"])]
        
        return {
            "total_products": len(df),
            "recommended_count": len(recommended),
            "high_rated_count": len(high_rated),
            "avg_profit": round(df["net_profit"].mean(), 2),
            "avg_profit_rate": round(df["profit_rate"].mean(), 2),
            "top_products": high_rated.head(20).to_dict('records'),
            "category_analysis": self._category_analysis(df),
            "all_products": products
        }
    
    def _category_analysis(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        if "category" not in df.columns:
            return []
        
        category_stats = df.groupby("category").agg({
            "net_profit": ["mean", "count"],
            "profit_rate": "mean"
        }).round(2)
        
        result = []
        for cat, row in category_stats.iterrows():
            result.append({
                "category": cat,
                "avg_profit": row[("net_profit", "mean")],
                "avg_rate": row[("profit_rate", "mean")],
                "product_count": row[("net_profit", "count")]
            })
        
        return sorted(result, key=lambda x: x["avg_profit"], reverse=True)
    
    def generate_selection_report(self, platform: str, analysis: Dict[str, Any]) -> str:
        top_products = analysis["top_products"]
        
        products_table = ""
        for p in top_products[:15]:
            products_table += f"| {p.get('title', '')[:30]} | {p.get('rating', '-')} | ¥{p.get('price', 0):.2f} | ¥{p.get('cost_price', 0):.2f} | **¥{p.get('net_profit', 0):.2f}** | {p.get('profit_rate', 0):.1f}% |\n"
        
        categories = analysis.get("category_analysis", [])
        category_table = ""
        for cat in categories[:8]:
            category_table += f"| {cat['category'][:15]} | {cat['product_count']} | ¥{cat['avg_profit']:.2f} | {cat['avg_rate']:.1f}% |\n"
        
        content = f"""---
title: {platform}选品分析报告
type: insight
platform: {platform}
created: {datetime.now().strftime('%Y-%m-%d')}
tags: ["选品", "电商", "{platform}", "利润分析"]
---

# {platform}选品分析报告

> 基于 {analysis['total_products']} 个商品数据分析
> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📊 选品概览

| 指标 | 数值 |
|------|------|
| 分析商品数 | {analysis['total_products']} 个 |
| ✅ 推荐选品数 | {analysis['recommended_count']} 个 |
| ⭐ S/A级商品 | {analysis['high_rated_count']} 个 |
| 平均净利润 | ¥{analysis['avg_profit']} |
| 平均利润率 | {analysis['avg_profit_rate']}% |

---

## 🏆 Top 选品推荐 (S/A级)

| 商品名称 | 评级 | 售价 | 估算成本 | 净利润 | 利润率 |
|----------|------|------|----------|--------|--------|
{products_table}

---

## 📂 品类利润分析

| 品类 | 商品数 | 平均利润 | 利润率 |
|------|--------|----------|--------|
{category_table if category_table else '| 待补充 | - | - | - |'}

---

## 💡 选品策略建议

1. **优先选择S/A级商品**：净利润¥30+，利润率35%+
2. **控制成本结构**：进货成本建议控制在售价的40%-50%
3. **避开竞争红海**：同款商品过多的谨慎进入
4. **考虑重量体积**：大件商品物流成本高，需调高售价

### 利润计算公式
```
净利润 = 售价 - 进货价 - 运费¥8 - 平台服务费6%
推荐标准：净利润¥20+ 且 利润率25%+
```

---

## 🎯 评级标准

| 评级 | 利润要求 | 利润率要求 |
|------|----------|------------|
| S级 | ¥50+ | 50%+ |
| A级 | ¥30+ | 35%+ |
| B级 | ¥20+ | 25%+ |
| C级 | ¥10+ | - |

---

*本报告由选品分析引擎自动生成*
"""
        return content
    
    def save_report(self, platform: str, products: List[Dict[str, Any]]) -> Path:
        analysis = self.analyze_products(products)
        report_content = self.generate_selection_report(platform, analysis)
        
        filepath = self.result_dir / f"{platform}选品SKILL.md"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(report_content)
        
        json_path = self.result_dir / f"{platform}_products_raw.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 选品报告已保存: {filepath.name}")
        return filepath
