import re
import json
from collections import Counter
from typing import List, Dict, Any, Tuple
from datetime import datetime
from pathlib import Path

import jieba
import jieba.analyse
import pandas as pd

from config import ANALYSIS_CONFIG, MEMORY_DIR


class HotContentAnalyzer:
    def __init__(self):
        import sys
        if sys.platform != "win32":
            jieba.enable_parallel(4)
        self.stop_words = self._load_stop_words()
        self.result_dir = MEMORY_DIR / "insights"
        self.result_dir.mkdir(exist_ok=True)
    
    def _load_stop_words(self) -> set:
        default = {"的", "了", "是", "在", "我", "有", "和", "就", "不", "人", "都", "一", "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会", "着", "没有", "看", "好", "自己", "这"}
        return default
    
    def extract_keywords(self, texts: List[str], top_k: int = 20) -> List[Tuple[str, float]]:
        all_text = " ".join(texts)
        keywords = jieba.analyse.extract_tags(
            all_text,
            topK=top_k,
            withWeight=True,
            allowPOS=('n', 'vn', 'v', 'a')
        )
        return keywords
    
    def extract_titles_keywords(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        titles = [item.get("title", "") for item in items]
        keywords = self.extract_keywords(titles, 30)
        
        hot_patterns = self._find_title_patterns(titles)
        
        return {
            "total_samples": len(titles),
            "keywords": [{"word": k, "weight": round(w, 4)} for k, w in keywords],
            "hot_patterns": hot_patterns,
            "analyzed_at": datetime.now().isoformat()
        }
    
    def _find_title_patterns(self, titles: List[str]) -> Dict[str, Any]:
        patterns = {
            "number_prefix": 0,
            "question_format": 0,
            "how_to": 0,
            "secret_pattern": 0,
            "profit_pattern": 0
        }
        
        for title in titles:
            title = str(title)
            if re.search(r'^\d', title):
                patterns["number_prefix"] += 1
            if re.search(r'[？?]$', title):
                patterns["question_format"] += 1
            if re.search(r'怎么|如何|怎样|如何|教程|步骤', title):
                patterns["how_to"] += 1
            if re.search(r'秘密|揭秘|内幕|不知道|真相', title):
                patterns["secret_pattern"] += 1
            if re.search(r'赚钱|利润|收入|月入|副业|创业', title):
                patterns["profit_pattern"] += 1
        
        total = len(titles) if len(titles) > 0 else 1
        return {k: {"count": v, "ratio": round(v / total * 100, 1)} for k, v in patterns.items()}
    
    def analyze_hot_rules(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        df = pd.DataFrame(items)
        
        if df.empty:
            return {"error": "无数据"}
        
        hot_threshold = df.get("play_count", pd.Series([0])).quantile(0.8)
        hot_items = df[df.get("play_count", 0) >= hot_threshold] if "play_count" in df.columns else df.head(20)
        
        result = {
            "overall": {
                "total_count": len(df),
                "hot_count": len(hot_items),
                "hot_threshold": int(hot_threshold),
                "avg_play": int(df.get("play_count", 0).mean()),
                "avg_like": int(df.get("like_count", 0).mean())
            },
            "title_analysis": self.extract_titles_keywords(hot_items.to_dict('records')),
            "best_length": self._analyze_title_length(items),
            "publish_hours": self._analyze_publish_time(items),
            "recommendations": []
        }
        
        result["recommendations"] = self._generate_recommendations(result)
        return result
    
    def _analyze_title_length(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        lengths = [len(str(item.get("title", ""))) for item in items]
        scores = [item.get("hot_score", 0) for item in items]
        
        length_groups = {}
        for length, score in zip(lengths, scores):
            group = f"{(length // 5) * 5}-{(length // 5 + 1) * 5}字"
            if group not in length_groups:
                length_groups[group] = []
            length_groups[group].append(score)
        
        avg_scores = {k: sum(v) / len(v) for k, v in length_groups.items() if len(v) >= 3}
        sorted_groups = sorted(avg_scores.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "best_performing": sorted_groups[:3],
            "avg_length": int(sum(lengths) / len(lengths))
        }
    
    def _analyze_publish_time(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {
            "note": "待完善发布时间分析",
            "recommended_hours": ["07:00-09:00", "12:00-14:00", "18:00-22:00"]
        }
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        recs = []
        patterns = analysis["title_analysis"]["hot_patterns"]
        
        if patterns["number_prefix"]["ratio"] > 30:
            recs.append("✅ 强烈推荐使用数字开头标题（效果最显著）")
        
        if patterns["profit_pattern"]["ratio"] > 20:
            recs.append("💰 '赚钱/收入/月入'等关键词转化率高")
        
        if patterns["how_to"]["ratio"] > 25:
            recs.append("📚 实用教程类标题点击率高")
        
        recs.extend([
            "📝 建议标题长度：15-25字",
            "🎯 发布时间：晚高峰18-22点效果最好",
            "#️⃣ 每篇带3-5个精准话题标签"
        ])
        
        return recs
    
    def generate_skill_note(self, platform: str, analysis: Dict[str, Any]) -> str:
        keywords_str = "\n".join([f"- {kw['word']}: {kw['weight']}" for kw in analysis["title_analysis"]["keywords"][:15]])
        
        patterns_str = ""
        for name, data in analysis["title_analysis"]["hot_patterns"].items():
            patterns_str += f"- {name}: {data['count']}次 ({data['ratio']}%)\n"
        
        recs_str = "\n".join(analysis["recommendations"])
        
        content = f"""---
title: {platform}爆款创作SKILL
type: insight
platform: {platform}
created: {datetime.now().strftime('%Y-%m-%d')}
tags: ["创作技巧", "爆款规律", "{platform}", "SKILL"]
---

# {platform}爆款创作SKILL

> 基于 {analysis['overall']['total_count']} 条爆款数据训练
> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 🎯 爆款核心关键词

{keywords_str}

---

## 📐 标题成功公式分析

| 模式 | 出现次数 | 占比 |
|------|----------|------|
"""
        
        for name, data in analysis["title_analysis"]["hot_patterns"].items():
            content += f"| {name} | {data['count']} | {data['ratio']}% |\n"
        
        content += f"""

---

## 💡 创作建议

{recs_str}

---

## 📊 数据概览

- 分析样本: {analysis['overall']['total_count']} 条
- 爆款门槛: {analysis['overall'].get('hot_threshold', 'N/A')} 播放
- 平均互动率: {analysis['overall']['avg_like'] / max(analysis['overall']['avg_play'], 1) * 100:.2f}%

---

*本SKILL由内容分析引擎自动生成，持续更新中*
"""
        return content
    
    def save_analysis(self, platform: str, items: List[Dict[str, Any]]) -> Path:
        analysis = self.analyze_hot_rules(items)
        skill_content = self.generate_skill_note(platform, analysis)
        
        filepath = self.result_dir / f"{platform}爆款创作SKILL.md"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(skill_content)
        
        json_path = self.result_dir / f"{platform}_analysis_raw.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
        
        print(f"✅ SKILL已保存: {filepath.name}")
        return filepath
