#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬虫Web操作界面
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import gradio as gr
import pandas as pd
import json
from loguru import logger

from config import DATA_DIR, MEMORY_DIR


def run_crawler(zimeiti_platforms, xiaomaibu_platforms, mode, limit, keyword, progress=gr.Progress()):
    all_results = []
    status_msgs = []
    keyword = keyword.strip() if keyword else None
    
    zimeiti_map = {
        "B站": "bilibili",
        "抖音": "douyin",
        "小红书": "xiaohongshu"
    }
    
    xiaomaibu_map = {
        "闲鱼": "xianyu",
        "1688": "1688",
        "拼多多": "pinduoduo"
    }
    
    selected_platforms = []
    for p in zimeiti_platforms:
        if p in zimeiti_map:
            selected_platforms.append(zimeiti_map[p])
    for p in xiaomaibu_platforms:
        if p in xiaomaibu_map:
            selected_platforms.append(xiaomaibu_map[p])
    
    if not selected_platforms:
        return pd.DataFrame(), "❌ 请至少选择一个平台！"
    
    progress(0, desc="开始抓取...")
    total = len(selected_platforms)
    
    for idx, platform in enumerate(selected_platforms):
        progress((idx) / total, desc=f"正在抓取: {platform}")
        
        if platform == "bilibili":
            from platforms.bilibili import BilibiliScraper
            from analyzers.content_analyzer import HotContentAnalyzer
            
            scraper = BilibiliScraper()
            data = scraper.run(mode=mode, limit=limit, sync=True, keyword=keyword)
            
            if data:
                analyzer = HotContentAnalyzer()
                analyzer.save_analysis(f"bilibili_{keyword}" if keyword else "bilibili", data)
                all_results.extend(data)
                status_msgs.append(f"✅ B站: {len(data)} 条")
        
        elif platform == "xiaohongshu":
            from platforms.xiaohongshu import XiaohongshuScraper
            from analyzers.content_analyzer import HotContentAnalyzer
            
            scraper = XiaohongshuScraper()
            data = scraper.run(mode=mode, limit=limit, sync=True, keyword=keyword)
            
            if data:
                analyzer = HotContentAnalyzer()
                analyzer.save_analysis(f"xiaohongshu_{keyword}" if keyword else "xiaohongshu", data)
                all_results.extend(data)
                status_msgs.append(f"✅ 小红书: {len(data)} 条")
        
        elif platform == "douyin":
            from platforms.douyin import DouyinScraper
            from analyzers.content_analyzer import HotContentAnalyzer
            
            scraper = DouyinScraper()
            data = scraper.run(mode=mode, limit=limit, sync=True, keyword=keyword)
            
            if data:
                analyzer = HotContentAnalyzer()
                analyzer.save_analysis(f"douyin_{keyword}" if keyword else "douyin", data)
                all_results.extend(data)
                status_msgs.append(f"✅ 抖音: {len(data)} 条")
        
        elif platform in ["xianyu", "1688", "pinduoduo"]:
            from scheduler.task_scheduler import TaskScheduler
            scheduler = TaskScheduler()
            scheduler.task_ecommerce_selection()
            status_msgs.append(f"✅ {platform}: 电商选品分析完成")
    
    progress(1.0, desc="完成！")
    
    if all_results:
        df = pd.DataFrame(all_results)
        display_cols = ["platform", "title", "author", "play_count", "like_count", "comment_count"]
        display_cols = [c for c in display_cols if c in df.columns]
        status_text = "\n".join(status_msgs) + f"\n\n📊 总计: {len(all_results)} 条数据\n📁 已自动同步到 Obsidian 知识库"
        return df[display_cols], status_text
    else:
        status_text = "\n".join(status_msgs) if status_msgs else "⚠️ 未获取到数据（检查Cookie配置）"
        return pd.DataFrame(), status_text


def get_history_files():
    insights = []
    insights_dir = MEMORY_DIR / "insights"
    if insights_dir.exists():
        for f in insights_dir.glob("*SKILL*.md"):
            insights.append((f.name, str(f)))
    return insights


def read_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "文件读取失败"


def create_ui():
    with gr.Blocks(title="GrabLab 爬虫控制台") as demo:
        gr.Markdown("""
        # 🚀 GrabLab 智能多平台爬虫控制台
        
        一站式社媒爆款分析 + 电商选品工具
        """)
        
        with gr.Tab("🎯 爬虫控制台"):
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### 📱 自媒体平台")
                    zimeiti_platforms = gr.CheckboxGroup(
                        label="选择平台（可多选）",
                        choices=["B站", "抖音", "小红书"],
                        value=["B站"],
                        interactive=True
                    )
                    
                    gr.Markdown("---")
                    gr.Markdown("### 🏪 小卖部平台")
                    xiaomaibu_platforms = gr.CheckboxGroup(
                        label="选择平台（可多选）",
                        choices=["闲鱼", "1688", "拼多多"],
                        value=[],
                        interactive=True
                    )
                    
                    gr.Markdown("---")
                    mode = gr.Dropdown(
                        label="抓取模式",
                        choices=["hot", "search"],
                        value="hot"
                    )
                    keyword = gr.Textbox(
                        label="搜索关键词（search模式）",
                        placeholder="输入要搜索的主题，如：AI 创业",
                        visible=True
                    )
                    limit = gr.Slider(
                        label="单平台抓取数量",
                        minimum=10,
                        maximum=200,
                        value=50,
                        step=10
                    )
                    run_btn = gr.Button("🚀 开始抓取", variant="primary", size="lg")
                
                with gr.Column(scale=2):
                    status = gr.Textbox(
                        label="运行状态",
                        lines=5,
                        interactive=False
                    )
                    output_df = gr.Dataframe(
                        label="抓取结果预览",
                        wrap=True
                    )
        
        with gr.Tab("📊 分析结果"):
            with gr.Row():
                file_list = gr.Dropdown(
                    label="已生成的SKILL文件",
                    choices=[f[0] for f in get_history_files()],
                    value=get_history_files()[0][0] if get_history_files() else None
                )
                refresh_btn = gr.Button("🔄 刷新列表")
            
            file_content = gr.Markdown(label="SKILL内容预览")
        
        with gr.Tab("⚙️ 配置说明"):
            gr.Markdown("""
            ## 🔑 Cookie 配置
            
            1. 复制 `.env.example` 为 `.env`
            2. 按照 `Cookie配置指南.md` 获取对应平台Cookie
            3. 填入后重启程序
            
            ## 📋 命令行使用
            
            ```bash
            # 热门内容
            python main.py -p bilibili -l 50
            
            # 关键词搜索
            python main.py -p bilibili -k "AI创业" -l 30
            
            # 启动Web界面
            python main.py -w
            ```
            
            ## 📁 数据位置
            
            | 目录 | 内容 |
            |------|------|
            | `sources/[平台]/` | 原始JSON数据 |
            | `memory/insights/` | 爆款创作SKILL |
            | `outputs/reports/` | 详细分析报告 |
            """)
        
        run_btn.click(
            fn=run_crawler,
            inputs=[zimeiti_platforms, xiaomaibu_platforms, mode, limit, keyword],
            outputs=[output_df, status]
        )
        
        def refresh_files():
            files = get_history_files()
            return gr.update(
                choices=[f[0] for f in files],
                value=files[0][0] if files else None
            )
        
        refresh_btn.click(fn=refresh_files, outputs=[file_list])
        
        def on_file_select(filename):
            files = get_history_files()
            filepath = next((f[1] for f in files if f[0] == filename), "")
            return read_file(filepath)
        
        file_list.change(fn=on_file_select, inputs=[file_list], outputs=[file_content])
    
    return demo


def run_webui():
    logger.info("启动 WebUI：http://localhost:7860")
    demo = create_ui()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        inbrowser=True
    )


if __name__ == "__main__":
    run_webui()
