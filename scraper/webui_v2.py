#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬虫Web操作界面 V2 - 全新架构版
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import gradio as gr
import pandas as pd
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
            from crawlers.bilibili_crawler import BilibiliScraper
            
            scraper = BilibiliScraper()
            data = scraper.run(mode=mode, limit=limit, sync=True, keyword=keyword)
            
            if data:
                all_results.extend(data)
                status_msgs.append(f"✅ B站: {len(data)} 条")
        
        elif platform == "xiaohongshu":
            from crawlers.xiaohongshu_crawler import XiaohongshuScraper
            
            scraper = XiaohongshuScraper()
            data = scraper.run(mode=mode, limit=limit, sync=True, keyword=keyword)
            
            if data:
                all_results.extend(data)
                status_msgs.append(f"✅ 小红书: {len(data)} 条")
        
        elif platform == "douyin":
            from crawlers.douyin_crawler import DouyinScraper
            
            scraper = DouyinScraper()
            data = scraper.run(mode=mode, limit=limit, sync=True, keyword=keyword)
            
            if data:
                all_results.extend(data)
                status_msgs.append(f"✅ 抖音: {len(data)} 条")
        
        elif platform in ["xianyu", "1688", "pinduoduo"]:
            status_msgs.append(f"✅ {platform}: 电商平台开发中")
    
    progress(1.0, desc="完成！")
    
    if all_results:
        df = pd.DataFrame(all_results)
        display_cols = ["platform", "title", "author", "play_count", "like_count", "comment_count"]
        display_cols = [c for c in display_cols if c in df.columns]
        status_text = "\n".join(status_msgs) + f"\n\n📊 总计: {len(all_results)} 条数据\n📁 JSON已保存到 data/ 目录\n📁 已自动同步到 Obsidian 知识库"
        return df[display_cols], status_text
    else:
        status_text = "\n".join(status_msgs) if status_msgs else "⚠️ 未获取到数据（检查Cookie配置）"
        return pd.DataFrame(), status_text


def create_ui():
    with gr.Blocks(title="GrabLab V2 - 专业爬虫控制台") as demo:
        gr.HTML("""
        <h1 style='text-align: center; color: #165DFF; margin-bottom: 20px;'>
            🚀 GrabLab 专业爬虫控制台 V2
        </h1>
        <p style='text-align: center; color: #666;'>
            工程级架构 · 标准化数据 · Obsidian知识库集成
        </p>
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
                        label="🔍 搜索关键词（search模式）",
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
                        lines=6,
                        interactive=False
                    )
                    output_df = gr.Dataframe(
                        label="抓取结果预览",
                        wrap=True
                    )
        
        with gr.Tab("⚙️ 配置说明"):
            gr.Markdown("""
            ## 🔑 Cookie 配置
            
            1. 打开 `.env` 文件
            2. 按照 `Cookie配置指南.md` 获取对应平台Cookie
            3. 填入后重启程序
            
            ## 📋 命令行使用
            
            ```bash
            # 热门内容
            python main.py -p bilibili -l 50
            
            # 关键词搜索
            python main.py -p bilibili -k "AI创业" -l 30
            
            # 启动Web界面
            python webui_v2.py
            ```
            
            ## 📁 数据位置
            
            | 目录 | 内容 |
            |------|------|
            | `sources/[平台]/` | 原始JSON数据 |
            | `memory/insights/` | 爆款创作SKILL |
            | `outputs/reports/` | 详细分析报告 |
            
            ## 🏗️ 系统架构
            
            - **crawlers/** - 爬虫模块
            - **parsers/** - 数据解析
            - **analyzers/** - 智能分析
            - **storages/** - 存储模块
            - **utils/** - 反爬+登录管理
            """)
        
        run_btn.click(
            fn=run_crawler,
            inputs=[zimeiti_platforms, xiaomaibu_platforms, mode, limit, keyword],
            outputs=[output_df, status]
        )
    
    return demo


def run_webui():
    logger.info("=" * 60)
    logger.info("  启动 WebUI V2：http://localhost:7861")
    logger.info("=" * 60)
    demo = create_ui()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7861,
        inbrowser=True
    )


if __name__ == "__main__":
    run_webui()
