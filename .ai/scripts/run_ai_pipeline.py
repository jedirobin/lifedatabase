#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 知识库流水线入口
用法: python run_ai_pipeline.py [step]
steps: ingest, compile, full
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import json
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent
BASE_DIR = SCRIPT_DIR.parent.parent

def print_banner():
    print("\n" + "=" * 60)
    print("  🤖 Trae AI 知识库自动化流水线")
    print("=" * 60)
    print(f"  时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

def run_ingest():
    """步骤1: 处理收件箱素材"""
    print("📥 步骤 1/2: 处理收件箱素材")
    print("-" * 50)
    
    sys.path.insert(0, str(SCRIPT_DIR))
    import ingest
    ingest.process_inbox()
    print()

def run_compile():
    """步骤2: 编译知识到memory"""
    print("📚 步骤 2/3: 知识编译")
    print("-" * 50)
    
    sys.path.insert(0, str(SCRIPT_DIR))
    import compile
    compile.compile_sources()
    print()

def run_graph():
    """步骤3: 构建知识图谱"""
    print("🔭 步骤 3/3: 构建 Karpathy 知识图谱")
    print("-" * 50)
    
    sys.path.insert(0, str(SCRIPT_DIR))
    import graph_builder
    kg = graph_builder.KnowledgeGraph()
    kg.build_from_sources()
    print()

def run_full():
    """完整流程"""
    print_banner()
    run_ingest()
    run_compile()
    run_graph()
    
    print("🎉 " + "=" * 50)
    print("   ✅ Karpathy Wiki 知识图谱构建完成！")
    print("=" * 50)
    print()
    print("💡 在 Obsidian 中探索：")
    print("   1. 打开 [[memory/index.md]] 浏览图谱索引")
    print("   2. 按 Cmd/Ctrl + G 查看知识图谱视图")
    print("   3. 点击任意 [[链接]] 漫游知识网络")
    print()
    print("💡 在 Trae 中：")
    print("   - 提问关于知识库的任意问题")
    print("   - 说「扩展知识图谱」补充新节点")
    print("   - 继续往 sources/inbox/ 扔新素材")
    print()

if __name__ == "__main__":
    step = sys.argv[1] if len(sys.argv) > 1 else "full"
    
    if step == "ingest":
        print_banner()
        run_ingest()
    elif step == "compile":
        print_banner()
        run_compile()
    elif step == "graph":
        print_banner()
        run_graph()
    else:
        run_full()
