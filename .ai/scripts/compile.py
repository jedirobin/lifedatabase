#!/usr/bin/env python3
"""
知识编译脚本 - 从sources提取知识更新memory
用法: python compile.py
"""
import os
import re
import json
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent
BASE_DIR = SCRIPT_DIR.parent.parent
SOURCES_DIR = BASE_DIR / "sources"
MEMORY_DIR = BASE_DIR / "memory"

def extract_title(content: str, filepath: Path) -> str:
    """从内容中提取标题"""
    lines = content.split('\n')
    for line in lines[:5]:  # 只看前5行
        if line.startswith('#'):
            return line.replace('#', '').strip()
    return filepath.stem

def extract_keywords(content: str) -> list:
    """简单提取关键词（可后续接入NLP）"""
    # 提取话题标签
    hashtags = re.findall(r'#(\w+)', content)
    # 提取人名（简单规则）
    names = re.findall(r'[\u4e00-\u9fa5]{2,4}', content)[:5]
    return list(set(hashtags + names))[:10]

def create_memory_entry(filepath: Path, content: str) -> dict:
    """创建memory条目"""
    title = extract_title(content, filepath)
    keywords = extract_keywords(content)
    
    return {
        'title': title,
        'source': str(filepath.relative_to(BASE_DIR)),
        'date': datetime.now().strftime("%Y-%m-%d"),
        'word_count': len(content),
        'keywords': keywords,
        'summary': content[:200] + '...' if len(content) > 200 else content
    }

def update_index(entries: list):
    """更新索引文件"""
    index_path = MEMORY_DIR / "index.md"
    
    header = """# 知识库索引

> 最后更新：{}

---

## 最近添加

""".format(datetime.now().strftime("%Y-%m-%d %H:%M"))
    
    content_lines = []
    for entry in entries[-20:]:  # 只显示最近20条
        content_lines.append(f"- [[{entry['title']}]] - {entry['date']} ({entry['word_count']}字)")
    
    full_content = header + '\n'.join(content_lines)
    index_path.write_text(full_content, encoding='utf-8')
    print(f"✅ 更新索引: {index_path}")

def compile_sources():
    """编译所有sources"""
    all_entries = []
    
    for source_type in ['articles', 'videos', 'podcasts', 'social']:
        type_dir = SOURCES_DIR / source_type
        if not type_dir.exists():
            continue
        
        for file in type_dir.rglob("*.md"):
            try:
                content = file.read_text(encoding='utf-8')
                entry = create_memory_entry(file, content)
                all_entries.append(entry)
            except Exception as e:
                print(f"⚠️ 处理失败: {file.name} - {e}")
    
    clippings_dir = BASE_DIR / "Clippings"
    if clippings_dir.exists():
        print(f"📰 处理网页剪藏: Clippings/")
        for file in clippings_dir.rglob("*.md"):
            try:
                content = file.read_text(encoding='utf-8')
                entry = create_memory_entry(file, content)
                all_entries.append(entry)
            except Exception as e:
                print(f"⚠️ 处理剪藏失败: {file.name} - {e}")
    
    if all_entries:
        update_index(all_entries)
        print(f"🎉 编译完成，共处理 {len(all_entries)} 个文件")
    else:
        print("📭 没有找到可编译的文件")

if __name__ == "__main__":
    print("=" * 50)
    print("📚 知识编译脚本")
    print("=" * 50)
    compile_sources()
