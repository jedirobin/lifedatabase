#!/usr/bin/env python3
"""
灵感库自动扩充脚本
每天从多个来源抓取创意点子，自动分类入库

来源：
- 知乎热榜（脑洞、故事类问题）
- 微博热搜（热点话题）
- 豆瓣小组（脑洞故事）
- 小红书（创意笔记）
- Reddit r/WritingPrompts

运行方式：
1. 本地运行：在 Trae 或本地终端执行
2. 结果会自动写入灵感库文件
3. 执行后 Git 提交推送
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path
import re
import hashlib

# ============ 配置 ============
BASE_DIR = Path(__file__).parent.parent
KEYWORDS_DIR = BASE_DIR / "灵感库" / "关键词"
STORY_DIR = BASE_DIR / "灵感库" / "故事模板"
GENG_DIR = BASE_DIR / "灵感库" / "梗库"
CACHE_FILE = BASE_DIR / ".ai" / "crawler_cache.json"
LOG_FILE = BASE_DIR / ".ai" / "crawler.log"

# ============ 工具函数 ============

def load_cache():
    """加载缓存，避免重复抓取"""
    if CACHE_FILE.exists():
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"processed": []}

def save_cache(cache):
    """保存缓存"""
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def log(message):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_entry + "\n")

def get_content_hash(content):
    """计算内容哈希"""
    return hashlib.md5(content.encode()).hexdigest()[:8]

def classify_content(title, content):
    """
    使用简单规则分类内容
    返回：(类型, 关键词列表)
    """
    text = f"{title} {content}".lower()
    
    # 关键词分类
    categories = {
        "职业": ["快递员", "医生", "程序员", "外卖", "主播", "教师", "警察", "司机"],
        "场景": ["深夜", "电梯", "便利店", "医院", "地铁", "网吧", "办公室"],
        "情绪": ["孤独", "温暖", "治愈", "恐惧", "感动", "遗憾", "希望"],
        "冲突": ["误会", "背叛", "救赎", "选择", "秘密", "谎言"],
        "反转": ["竟然是", "其实是", "原来", "没想到", "真相是"]
    }
    
    found_keywords = []
    found_category = "概念"
    
    for cat, keywords in categories.items():
        for kw in keywords:
            if kw in text:
                found_keywords.append(kw)
                found_category = cat
    
    return found_category, found_keywords

def extract_story_elements(title, content):
    """提取故事元素"""
    elements = {
        "标题": title,
        "核心设定": "",
        "关键词": [],
        "来源": "",
        "抓取时间": datetime.now().strftime("%Y-%m-%d")
    }
    
    # 尝试提取核心设定（简化版）
    if "如果" in content:
        match = re.search(r"如果(.{5,30})", content)
        if match:
            elements["核心设定"] = f"如果{match.group(1)}"
    
    if "可以" in content and "会怎样" in content:
        match = re.search(r"(.{3,20})可以(.{3,20})会怎样", content)
        if match:
            elements["核心设定"] = f"{match.group(1)}可以{match.group(2)}会怎样"
    
    return elements

# ============ 数据源爬虫 ============

def crawl_zhihu():
    """爬取知乎热榜"""
    log("开始爬取知乎热榜...")
    
    results = []
    try:
        # 知乎热榜 API
        url = "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            for item in data.get("data", [])[:20]:  # 取前20条
                target = item.get("target", {})
                title = target.get("title", "")
                excerpt = target.get("excerpt", "")
                
                # 筛选脑洞/故事类问题
                keywords = ["如果", "会怎样", "故事", "脑洞", "穿越", "魔法", "超能力", "时间", "假设"]
                if any(kw in title for kw in keywords):
                    results.append({
                        "title": title,
                        "content": excerpt,
                        "source": "知乎",
                        "url": f"https://www.zhihu.com/question/{target.get('id', '')}"
                    })
        
        log(f"知乎热榜获取 {len(results)} 条有效内容")
    except Exception as e:
        log(f"知乎爬取失败: {e}")
    
    return results

def crawl_weibo():
    """爬取微博热搜"""
    log("开始爬取微博热搜...")
    
    results = []
    try:
        # 使用公开的热搜 API
        url = "https://weibo.com/ajax/side/hotSearch"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            hot_list = data.get("data", {}).get("realtime", [])
            
            for item in hot_list[:30]:
                title = item.get("word", "")
                label = item.get("label", "")
                
                # 筛选有趣的话题
                skip_keywords = ["明星", "代言", "综艺", "直播", "带货"]
                if any(kw in title for kw in skip_keywords):
                    continue
                
                results.append({
                    "title": title,
                    "content": label,
                    "source": "微博",
                    "url": f"https://s.weibo.com/weibo?q={title}"
                })
        
        log(f"微博热搜获取 {len(results)} 条有效内容")
    except Exception as e:
        log(f"微博爬取失败: {e}")
    
    return results

def crawl_douban():
    """爬取豆瓣小组"""
    log("开始爬取豆瓣小组...")
    
    results = []
    try:
        # 豆瓣"脑洞"小组
        groups = [
            "brainhole",  # 脑洞小组
            "story",      # 故事小组
        ]
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        for group in groups:
            url = f"https://www.douban.com/group/{group}/topics"
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    # 简单解析（实际需要更复杂的解析）
                    text = response.text
                    # 提取标题（简化版）
                    titles = re.findall(r'<a[^>]*class="[^"]*title[^"]*"[^>]*>([^<]+)</a>', text)
                    
                    for title in titles[:10]:
                        title = title.strip()
                        if len(title) > 5 and len(title) < 50:
                            results.append({
                                "title": title,
                                "content": "",
                                "source": "豆瓣",
                                "url": url
                            })
            except:
                pass
        
        log(f"豆瓣小组获取 {len(results)} 条有效内容")
    except Exception as e:
        log(f"豆瓣爬取失败: {e}")
    
    return results

def crawl_xiaohongshu():
    """爬取小红书（模拟）"""
    log("小红书需要登录，跳过直接爬取，使用预设数据...")
    
    # 小红书需要登录，无法直接爬取
    # 这里返回空，后续可以考虑用云手机自动化
    return []

def crawl_writing_prompts():
    """爬取 Reddit WritingPrompts"""
    log("开始爬取 Reddit WritingPrompts...")
    
    results = []
    try:
        url = "https://www.reddit.com/r/WritingPrompts/hot.json"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            posts = data.get("data", {}).get("children", [])
            
            for post in posts[:15]:
                post_data = post.get("data", {})
                title = post_data.get("title", "")
                selftext = post_data.get("selftext", "")
                
                # 提取提示词（去掉 [WP] 等标签）
                title = re.sub(r'\[WP\]|\[IP\]|\[CW\]', '', title).strip()
                
                if len(title) > 10:
                    results.append({
                        "title": title,
                        "content": selftext[:200] if selftext else "",
                        "source": "Reddit",
                        "url": f"https://reddit.com{post_data.get('permalink', '')}"
                    })
        
        log(f"Reddit 获取 {len(results)} 条有效内容")
    except Exception as e:
        log(f"Reddit 爬取失败: {e}")
    
    return results

# ============ 写入灵感库 ============

def append_to_keywords_file(category, keywords, source_title):
    """追加关键词到对应文件"""
    file_map = {
        "职业": "人物.md",
        "场景": "场景.md",
        "情绪": "情绪.md",
        "冲突": "冲突.md"
    }
    
    filename = file_map.get(category, "概念.md")
    filepath = KEYWORDS_DIR / filename
    
    if not keywords:
        return
    
    # 读取现有内容
    existing = ""
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            existing = f.read()
    
    # 追加新关键词（去重）
    new_entries = []
    for kw in keywords:
        if kw and kw not in existing:
            new_entries.append(f"- {kw}")
    
    if new_entries:
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(f"\n# 来源: {source_title}\n")
            f.write("\n".join(new_entries) + "\n")
        log(f"  追加 {len(new_entries)} 个关键词到 {filename}")

def append_to_story_templates(title, core_idea, source):
    """追加故事模板"""
    if not core_idea:
        return
    
    filepath = STORY_DIR / "脑洞公式.md"
    
    # 读取现有内容
    existing = ""
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            existing = f.read()
    
    # 检查是否已存在
    if core_idea in existing:
        return
    
    # 追加
    with open(filepath, 'a', encoding='utf-8') as f:
        f.write(f"\n### {title}\n")
        f.write(f"**来源**: {source}\n")
        f.write(f"**核心设定**: {core_idea}\n")
        f.write(f"**抓取时间**: {datetime.now().strftime('%Y-%m-%d')}\n")
    
    log(f"  追加故事模板: {title[:20]}...")

def append_to_gengku(title, content, source):
    """追加梗到梗库"""
    # 检测是否包含反转元素
    reversal_keywords = ["竟然是", "其实是", "原来", "没想到", "反转", "结局"]
    
    if not any(kw in content for kw in reversal_keywords):
        return
    
    filepath = GENG_DIR / "反转套路.md"
    
    existing = ""
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            existing = f.read()
    
    if title in existing:
        return
    
    with open(filepath, 'a', encoding='utf-8') as f:
        f.write(f"\n### {title}\n")
        f.write(f"**来源**: {source}\n")
        f.write(f"**内容**: {content[:100]}...\n")
        f.write(f"**抓取时间**: {datetime.now().strftime('%Y-%m-%d')}\n")
    
    log(f"  追加梗到梗库: {title[:20]}...")

# ============ 主流程 ============

def main():
    print("=" * 50)
    print("灵感库自动扩充 - 开始运行")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # 加载缓存
    cache = load_cache()
    
    # 确保目录存在
    KEYWORDS_DIR.mkdir(parents=True, exist_ok=True)
    STORY_DIR.mkdir(parents=True, exist_ok=True)
    GENG_DIR.mkdir(parents=True, exist_ok=True)
    
    # 爬取所有来源
    all_items = []
    all_items.extend(crawl_zhihu())
    all_items.extend(crawl_weibo())
    all_items.extend(crawl_douban())
    all_items.extend(crawl_xiaohongshu())
    all_items.extend(crawl_writing_prompts())
    
    log(f"总共获取 {len(all_items)} 条原始内容")
    
    # 处理并入库
    new_count = 0
    for item in all_items:
        content_hash = get_content_hash(item["title"])
        
        # 检查是否已处理
        if content_hash in cache["processed"]:
            continue
        
        title = item.get("title", "")
        content = item.get("content", "")
        source = item.get("source", "未知")
        
        log(f"处理: {title[:30]}...")
        
        # 分类
        category, keywords = classify_content(title, content)
        
        # 写入对应库
        append_to_keywords_file(category, keywords, title)
        
        # 提取故事元素
        elements = extract_story_elements(title, content)
        if elements["核心设定"]:
            append_to_story_templates(title, elements["核心设定"], source)
        
        # 写入梗库
        append_to_gengku(title, content, source)
        
        # 标记已处理
        cache["processed"].append(content_hash)
        new_count += 1
    
    # 保存缓存
    save_cache(cache)
    
    # 生成摘要报告
    log(f"\n本次新增 {new_count} 条灵感素材")
    log("=" * 50)
    log("灵感库扩充完成！")
    
    return {
        "total": len(all_items),
        "new": new_count,
        "sources": ["知乎", "微博", "豆瓣", "Reddit"]
    }

if __name__ == "__main__":
    result = main()
    print(f"\n摘要: 获取 {result['total']} 条，新增 {result['new']} 条")
