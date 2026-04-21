#!/usr/bin/env python3
"""
素材处理脚本 - 自动导入inbox中的新素材
用法: python ingest.py
"""
import os
import shutil
from pathlib import Path
from datetime import datetime

# 获取脚本所在目录，然后定位到知识库根目录
SCRIPT_DIR = Path(__file__).parent
BASE_DIR = SCRIPT_DIR.parent.parent
INBOX_DIR = BASE_DIR / "sources" / "inbox"
SOURCES_DIR = BASE_DIR / "sources"

def get_file_type(filename: str) -> str:
    """根据扩展名判断文件类型"""
    ext = Path(filename).suffix.lower()
    type_map = {
        '.pdf': 'pdfs',
        '.ppt': 'ppts', '.pptx': 'ppts',
        '.mp3': 'podcasts', '.wav': 'podcasts', '.m4a': 'podcasts',
        '.mp4': 'videos', '.mkv': 'videos', '.avi': 'videos',
        '.md': 'articles', '.txt': 'articles',
        '.json': 'data',
    }
    return type_map.get(ext, 'articles')

def process_inbox():
    """处理inbox中的所有文件"""
    if not INBOX_DIR.exists():
        INBOX_DIR.mkdir(parents=True)
        print("📁 创建inbox目录")
        return
    
    processed = 0
    for file in INBOX_DIR.iterdir():
        if file.is_file() and not file.name.startswith('.'):
            file_type = get_file_type(file.name)
            target_dir = SOURCES_DIR / file_type
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # 添加日期前缀
            date_prefix = datetime.now().strftime("%Y%m%d")
            new_name = f"{date_prefix}_{file.name}"
            target_path = target_dir / new_name
            
            # 避免重名
            if target_path.exists():
                new_name = f"{date_prefix}_{datetime.now().strftime('%H%M%S')}_{file.name}"
                target_path = target_dir / new_name
            
            shutil.move(str(file), str(target_path))
            print(f"✅ 移动: {file.name} → {file_type}/{new_name}")
            processed += 1
    
    if processed == 0:
        print("📭 inbox为空，没有需要处理的文件")
    else:
        print(f"🎉 处理完成，共移动 {processed} 个文件")

if __name__ == "__main__":
    print("=" * 50)
    print("📥 素材处理脚本")
    print("=" * 50)
    process_inbox()
