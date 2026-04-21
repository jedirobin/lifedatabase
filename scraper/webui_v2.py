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


def data_to_document(data_list, show_detail: bool = True):
    if not data_list:
        return "暂无数据"
    
    doc = []
    doc.append(f"# 抓取结果汇总")
    total_comments = sum(len(v.get('comments', [])) for v in data_list)
    total_danmaku = sum(len(v.get('danmaku', [])) for v in data_list)
    doc.append(f"\n📊 总计: **{len(data_list)}** 条视频")
    doc.append(f"\n💬 抓取评论: **{total_comments}** 条")
    doc.append(f"\n📝 抓取弹幕: **{total_danmaku}** 条\n")
    
    for idx, item in enumerate(data_list[:20], 1):
        platform = item.get('platform', '').upper()
        title = item.get('video_info', {}).get('title', '') or item.get('title', '')
        
        author_data = item.get('author', {})
        if isinstance(author_data, dict):
            author = author_data.get('name', '')
            fans_count = author_data.get('fans_count', 0)
        else:
            author = str(author_data)
            fans_count = 0
        
        views = item.get('stats', {}).get('view_count', 0) or item.get('play_count', 0)
        likes = item.get('stats', {}).get('like_count', 0) or item.get('like_count', 0)
        comment_count = item.get('stats', {}).get('comment_count', 0) or item.get('comment_count', 0)
        category = item.get('category', '')
        publish_time_str = item.get('publish_time_str', '')
        url = item.get('video_info', {}).get('video_url', '') or item.get('url', '')
        
        fetched_comments = item.get('comments', [])
        fetched_danmaku = item.get('danmaku', [])
        tags = item.get('tags', [])
        
        doc.append(f"\n---\n")
        doc.append(f"### {idx}. 【{platform}】{title}\n")
        doc.append(f"- 👤 作者: **{author}** | 粉丝: **{fans_count:,}**\n")
        if category:
            doc.append(f"- 📂 分区: **{category}**\n")
        if publish_time_str:
            doc.append(f"- 📅 发布时间: **{publish_time_str}**\n")
        doc.append(f"- 👁️ 播放: **{views:,}** | ❤️ 点赞: **{likes:,}**\n")
        if tags:
            doc.append(f"- 🏷️ 标签: **{', '.join(tags[:5])}**\n")
        doc.append(f"- 💬 评论总数: **{comment_count:,}** | 已抓取: **{len(fetched_comments)}** 条\n")
        doc.append(f"- 📝 弹幕已抓取: **{len(fetched_danmaku)}** 条\n")
        if url:
            doc.append(f"- 🔗 链接: [{url}]({url})\n")
        
        if show_detail and fetched_comments:
            doc.append(f"\n#### 💡 热门评论 (Top 5)\n")
            for c_idx, comment in enumerate(fetched_comments[:5], 1):
                content = comment.get('content', '')
                c_author = comment.get('author', '')
                c_likes = comment.get('like_count', 0)
                doc.append(f"{c_idx}. **@{c_author}** (❤️ {c_likes})\n")
                doc.append(f"   > {content}\n\n")
        
        if show_detail and fetched_danmaku:
            doc.append(f"\n#### 🔥 精选弹幕 (Top 10)\n")
            unique_danmaku = list({d.get('content', '') for d in fetched_danmaku[:50]})[:10]
            for dm in unique_danmaku:
                if dm.strip():
                    doc.append(f"> 🎬 {dm}\n")
                    doc.append(f"\n")
    
    doc.append(f"\n---\n")
    doc.append(f"\n💡 完整数据（含全部评论弹幕）已保存到 JSON 文件和 Obsidian 知识库")
    
    return "\n".join(doc)


def run_crawler(zimeiti_platforms, xiaomaibu_platforms, mode, limit, keyword, fetch_comments, fetch_danmaku, progress=gr.Progress()):
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
        return pd.DataFrame(), "❌ 请至少选择一个平台！", ""
    
    progress(0, desc="开始抓取...")
    total = len(selected_platforms)
    
    for idx, platform in enumerate(selected_platforms):
        progress((idx) / total, desc=f"正在抓取: {platform}")
        
        try:
            if platform == "bilibili":
                from crawlers.bilibili_crawler import BilibiliScraper
                
                scraper = BilibiliScraper()
                scraper.fetch_comments = fetch_comments
                scraper.fetch_danmaku = fetch_danmaku
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
        
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            if str(e).strip() and str(e) != "0":
                status_msgs.append(f"❌ {platform}: 出错 - {str(e)[:100]}")
    
    progress(1.0, desc="完成！")
    
    document = data_to_document(all_results)
    
    display_data = []
    for item in all_results:
        author_data = item.get('author', {})
        if isinstance(author_data, dict):
            author = author_data.get('name', '')
            fans_count = author_data.get('fans_count', 0)
        else:
            author = str(author_data)
            fans_count = 0
        
        row = {
            "平台": item.get('platform', '').upper(),
            "标题": item.get('video_info', {}).get('title', '') or item.get('title', ''),
            "作者": author,
            "作者粉丝": fans_count,
            "分区": item.get('category', ''),
            "播放量": item.get('stats', {}).get('view_count', 0) or item.get('play_count', 0),
            "点赞数": item.get('stats', {}).get('like_count', 0) or item.get('like_count', 0),
            "已抓评论": len(item.get('comments', [])),
            "已抓弹幕": len(item.get('danmaku', []))
        }
        display_data.append(row)
    
    if display_data:
        df = pd.DataFrame(display_data)
        total_comments = sum(len(v.get('comments', [])) for v in all_results)
        total_danmaku = sum(len(v.get('danmaku', [])) for v in all_results)
        status_lines = []
        if status_msgs:
            status_lines.extend(status_msgs)
        status_lines.extend([
            "",
            f"✅ 总计: {len(all_results)} 条内容",
            f"💬 抓取评论: {total_comments} 条",
            f"📝 抓取弹幕: {total_danmaku} 条",
            "📁 JSON已保存到 sources/ 目录",
            "📁 已自动同步到 Obsidian 知识库"
        ])
        status_text = "\n".join(status_lines)
        return df, status_text, document
    else:
        status_lines = []
        if status_msgs:
            status_lines.extend(status_msgs)
        status_lines.append("")
        if not status_msgs:
            status_lines.append("⚠️ 未获取到数据")
            status_lines.append("💡 建议:")
            status_lines.append("   1. 试试「热门内容」模式")
            status_lines.append("   2. 减少抓取条数")
            status_lines.append("   3. 如果频繁出现412错误，请配置Cookie")
        status_text = "\n".join(status_lines)
        return pd.DataFrame(), status_text, document


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
                        value=20,
                        step=10
                    )
                    
                    gr.Markdown("---")
                    gr.Markdown("### 🔬 深度抓取选项")
                    fetch_comments = gr.Checkbox(
                        label="抓取评论区（每条视频最多100条）",
                        value=True
                    )
                    fetch_danmaku = gr.Checkbox(
                        label="抓取弹幕内容（每条视频最多500条）",
                        value=True
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
        
        with gr.Tab("📄 文档预览"):
            gr.Markdown("### 整理好的抓取结果")
            document_view = gr.Markdown(label="文档内容")
        
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
            inputs=[zimeiti_platforms, xiaomaibu_platforms, mode, limit, keyword, fetch_comments, fetch_danmaku],
            outputs=[output_df, status, document_view]
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
