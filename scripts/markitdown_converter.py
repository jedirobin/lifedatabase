#!/usr/bin/env python3
"""
MarkItDown 自动转码脚本
功能：扫描待转码目录，转换文件为Markdown，归档原文件
"""

import os
import sys
import shutil
import logging
from datetime import datetime
from pathlib import Path

# 导入MarkItDown
from markitdown import MarkItDown

# ========== 配置 ==========
BASE_DIR = Path(__file__).parent.parent.resolve()  # ~/lifedatabase
SOURCES_DIR = BASE_DIR / "sources"
INPUT_DIR = SOURCES_DIR / "待转码"
OUTPUT_DIR = SOURCES_DIR / "待转码" / "output"
ARCHIVED_DIR = SOURCES_DIR / "已转码"
LOG_FILE = BASE_DIR / ".ai" / "convert.log"

# 支持的文件扩展名
SUPPORTED_EXTENSIONS = {
    '.pdf', '.docx', '.pptx', '.xlsx', '.xls',
    '.html', '.htm', '.csv', '.json', '.xml',
    '.epub', '.zip', '.jpg', '.jpeg', '.png', '.gif',
    '.mp3', '.wav', '.msg'
}

# ========== 日志配置 ==========
def setup_logging():
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

# ========== Git操作 ==========
def git_commit_and_push(logger):
    """Git提交并推送转换结果"""
    try:
        import subprocess
        repo_dir = BASE_DIR
        
        # 检查是否有变更
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            cwd=repo_dir,
            capture_output=True,
            text=True
        )
        
        if not result.stdout.strip():
            logger.info("没有需要提交的变更")
            return
        
        # Git add
        subprocess.run(['git', 'add', '-A'], cwd=repo_dir, check=True)
        
        # Git commit
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commit_msg = f"auto: MarkItDown转换 {timestamp}"
        subprocess.run(
            ['git', 'commit', '-m', commit_msg],
            cwd=repo_dir,
            check=True
        )
        
        # Git push
        subprocess.run(['git', 'push'], cwd=repo_dir, check=True)
        logger.info("Git提交并推送成功")
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Git操作失败: {e}")
    except Exception as e:
        logger.error(f"Git操作异常: {e}")

# ========== 核心转换逻辑 ==========
def convert_file(file_path: Path, output_dir: Path, logger) -> bool:
    """
    转换单个文件
    返回: 是否转换成功
    """
    md = MarkItDown()
    output_name = file_path.stem + ".md"  # 原文件名去除扩展名
    output_path = output_dir / output_name
    
    try:
        result = md.convert(str(file_path))
        content = result.text_content
        
        # 写入Markdown文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# {file_path.stem}\n\n")
            f.write(content)
        
        logger.info(f"转换成功: {file_path.name} -> {output_name}")
        return True
        
    except Exception as e:
        logger.error(f"转换失败 [{file_path.name}]: {str(e)}")
        return False

# ========== 主流程 ==========
def main():
    logger = setup_logging()
    logger.info("=" * 50)
    logger.info("MarkItDown 转换脚本启动")
    
    # 确保输出目录存在
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 统计
    total = 0
    success = 0
    failed = 0
    skipped = 0
    
    # 扫描待转码目录
    for item in INPUT_DIR.iterdir():
        # 跳过目录和README
        if item.is_dir() or item.name == "README.md":
            continue
        
        # 跳过不支持的文件
        if item.suffix.lower() not in SUPPORTED_EXTENSIONS:
            logger.warning(f"不支持的文件格式，跳过: {item.name}")
            skipped += 1
            continue
        
        total += 1
        logger.info(f"处理文件: {item.name}")
        
        # 转换文件
        if convert_file(item, OUTPUT_DIR, logger):
            success += 1
            # 转换成功后移动原文件到归档目录
            try:
                shutil.move(str(item), str(ARCHIVED_DIR / item.name))
                logger.info(f"已归档: {item.name}")
            except Exception as e:
                logger.error(f"归档失败 [{item.name}]: {str(e)}")
        else:
            failed += 1
            # 转换失败，保留原文件在原位置
    
    # 输出统计
    logger.info("-" * 50)
    logger.info(f"处理完成: 共{total}个文件, 成功{success}, 失败{failed}, 跳过{skipped}")
    
    # 如果有成功转换的文件，执行Git提交
    if success > 0:
        git_commit_and_push(logger)
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
