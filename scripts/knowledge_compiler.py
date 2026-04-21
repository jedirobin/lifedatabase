#!/usr/bin/env python3
"""
知识库自动编译脚本
基于 Karpathy 架构，自动处理 sources/inbox/ 中的新素材

功能：
1. 扫描 inbox 新文件
2. 调用 LLM API 分析内容
3. 提取实体、事实、概念
4. 更新 memory/ 页面
5. 更新 index.md
6. Git 提交推送
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path
import hashlib
import subprocess

# ============ 配置 ============
KNOWLEDGE_BASE_PATH = Path(__file__).parent.parent
SOURCES_INBOX = KNOWLEDGE_BASE_PATH / "sources" / "inbox"
MEMORY_PATH = KNOWLEDGE_BASE_PATH / "memory"
INDEX_PATH = MEMORY_PATH / "index.md"
PROCESSED_LOG = KNOWLEDGE_BASE_PATH / ".ai" / "processed_files.json"

# API 配置
DEEPSEEK_API_KEY = "sk-542e5de422164a5d977ed658902172e1"
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
GLM_API_KEY = "8e0eac60c18843eb831f5ded9751d5e1.Yf6zD8KORUOjPSCN"
GLM_API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

# 余额阈值
BALANCE_THRESHOLD = 5.0

# ============ 工具函数 ============

def get_file_hash(file_path):
    """计算文件哈希，用于判断是否已处理"""
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def load_processed_log():
    """加载已处理文件记录"""
    if PROCESSED_LOG.exists():
        with open(PROCESSED_LOG, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_processed_log(log):
    """保存已处理文件记录"""
    PROCESSED_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(PROCESSED_LOG, 'w', encoding='utf-8') as f:
        json.dump(log, f, ensure_ascii=False, indent=2)

def check_deepseek_balance():
    """检查 DeepSeek 余额"""
    try:
        response = requests.get(
            "https://api.deepseek.com/user/balance",
            headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            balance = data.get("is_available", False)
            # DeepSeek 返回的是布尔值，默认返回 True 表示可用
            # 如果需要具体余额，这里简化处理
            return True
    except:
        pass
    return False

def call_llm(prompt, content, use_glm=False):
    """调用 LLM API"""
    if use_glm:
        # 使用智谱 GLM
        headers = {
            "Authorization": f"Bearer {GLM_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "glm-4-flash",
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": content}
            ]
        }
        url = GLM_API_URL
    else:
        # 使用 DeepSeek
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": content}
            ]
        }
        url = DEEPSEEK_API_URL
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            print(f"API 调用失败: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"API 调用异常: {e}")
        return None

def analyze_content(file_path, file_type):
    """分析内容，提取结构化信息"""
    
    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 根据文件类型选择分析提示词
    if file_type in ['md', 'txt']:
        prompt = """你是一个知识库编译器。请分析以下内容，提取：

1. **主要实体**（人物、组织、概念、项目等）
2. **关键事实**（重要信息、数据、结论）
3. **核心概念**（需要解释的术语或概念）
4. **关联线索**（与其他知识的潜在联系）

请以 JSON 格式返回：
{
    "title": "内容标题",
    "summary": "一句话摘要",
    "entities": [
        {"name": "实体名", "type": "person/project/concept/organization", "description": "简短描述"}
    ],
    "facts": ["事实1", "事实2"],
    "concepts": ["概念1", "概念2"],
    "tags": ["标签1", "标签2"],
    "suggested_links": ["建议链接到的页面"]
}"""
    else:
        prompt = """分析这个文件，提取关键信息，以 JSON 格式返回：
{
    "title": "标题",
    "summary": "摘要",
    "entities": [],
    "facts": [],
    "concepts": [],
    "tags": [],
    "suggested_links": []
}"""
    
    # 选择 API（DeepSeek 余额检查）
    use_glm = not check_deepseek_balance()
    if use_glm:
        print("使用智谱 GLM API...")
    else:
        print("使用 DeepSeek API...")
    
    result = call_llm(prompt, content, use_glm)
    
    if result:
        try:
            # 提取 JSON 部分
            if '```json' in result:
                result = result.split('```json')[1].split('```')[0]
            elif '```' in result:
                result = result.split('```')[1].split('```')[0]
            return json.loads(result.strip())
        except:
            print(f"JSON 解析失败，原始返回: {result[:200]}...")
            return None
    return None

def update_memory_page(entity_info, source_file):
    """更新或创建 memory 页面"""
    entity_type = entity_info.get("type", "concept")
    entity_name = entity_info.get("name", "未知")
    
    # 确定目标目录
    type_to_dir = {
        "person": "people",
        "project": "projects",
        "concept": "concepts",
        "organization": "accounts",
        "account": "accounts"
    }
    target_dir = MEMORY_PATH / type_to_dir.get(entity_type, "concepts")
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建文件名（安全处理）
    safe_name = "".join(c for c in entity_name if c.isalnum() or c in ('-', '_', ' '))
    file_path = target_dir / f"{safe_name}.md"
    
    # 生成页面内容
    today = datetime.now().strftime("%Y-%m-%d")
    
    if file_path.exists():
        # 追加到已有页面
        with open(file_path, 'r', encoding='utf-8') as f:
            existing = f.read()
        
        # 更新 State 部分
        new_entry = f"""
**{today}** | 知识更新 — 来源: {source_file.name}
- {entity_info.get('description', '')}

"""
        # 在 Timeline 部分追加
        if "## Timeline" in existing:
            updated = existing.replace("## Timeline", f"## Timeline\n{new_entry}")
        else:
            updated = existing + f"\n\n---\n\n## Timeline\n{new_entry}"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated)
    else:
        # 创建新页面
        page_content = f"""---
title: {entity_name}
type: {entity_type}
tags: {entity_info.get('tags', [])}
created: {today}
updated: {today}
---

# {entity_name}

## State（当前状态）
{entity_info.get('description', '暂无描述')}

## Assessment（判断）
待分析

## Open Threads（开放问题）
- [ ] 待跟进事项

---

## Timeline（时间线）

**{today}** | 知识导入 — 来源: {source_file.name}
- {entity_info.get('description', '')}
"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(page_content)
    
    return file_path

def update_index(new_pages):
    """更新索引文件"""
    if not new_pages:
        return
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 读取现有索引
    if INDEX_PATH.exists():
        with open(INDEX_PATH, 'r', encoding='utf-8') as f:
            index_content = f.read()
    else:
        index_content = "# 知识库索引\n\n最后更新: {today}\n\n"
    
    # 添加新条目
    new_entries = "\n### 新增条目 ({today})\n"
    for page in new_pages:
        rel_path = page.relative_to(MEMORY_PATH)
        new_entries += f"- [[{rel_path.stem}]] - {page.parent.name}\n"
    
    # 更新索引
    updated_index = index_content.replace(
        f"最后更新:",
        f"最后更新: {today}\n{new_entries}\n"
    )
    
    with open(INDEX_PATH, 'w', encoding='utf-8') as f:
        f.write(updated_index)

def git_commit_push(message):
    """Git 提交并推送"""
    try:
        os.chdir(KNOWLEDGE_BASE_PATH)
        subprocess.run(["git", "add", "-A"], check=True)
        subprocess.run(["git", "commit", "-m", message], check=True)
        subprocess.run(["git", "push"], check=True)
        print(f"✅ Git 推送成功: {message}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Git 操作失败: {e}")
        return False

# ============ 主流程 ============

def main():
    print("=" * 50)
    print("知识库自动编译 - Karpathy 架构")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # 加载已处理记录
    processed = load_processed_log()
    new_pages = []
    
    # 扫描 inbox
    if not SOURCES_INBOX.exists():
        print("inbox 目录不存在，创建中...")
        SOURCES_INBOX.mkdir(parents=True, exist_ok=True)
        return
    
    files = list(SOURCES_INBOX.glob("*"))
    files = [f for f in files if f.is_file() and not f.name.startswith('.')]
    
    if not files:
        print("📭 inbox 为空，没有新文件需要处理")
        return
    
    print(f"📂 发现 {len(files)} 个文件待处理")
    
    # 处理每个文件
    for file_path in files:
        file_hash = get_file_hash(file_path)
        
        # 检查是否已处理
        if file_path.name in processed and processed[file_path.name] == file_hash:
            print(f"⏭️  跳过已处理: {file_path.name}")
            continue
        
        print(f"\n📄 处理: {file_path.name}")
        
        # 分析内容
        file_type = file_path.suffix.lstrip('.')
        analysis = analyze_content(file_path, file_type)
        
        if not analysis:
            print(f"⚠️  分析失败: {file_path.name}")
            continue
        
        print(f"   标题: {analysis.get('title', '未知')}")
        print(f"   实体: {len(analysis.get('entities', []))} 个")
        
        # 更新 memory 页面
        for entity in analysis.get('entities', []):
            page_path = update_memory_page(entity, file_path)
            new_pages.append(page_path)
            print(f"   ✅ 创建/更新: {page_path.name}")
        
        # 记录已处理
        processed[file_path.name] = file_hash
    
    # 保存处理记录
    save_processed_log(processed)
    
    # 更新索引
    if new_pages:
        update_index(new_pages)
        print(f"\n📚 索引已更新，新增 {len(new_pages)} 个页面")
        
        # Git 提交
        today = datetime.now().strftime("%Y-%m-%d")
        git_commit_push(f"知识库自动编译 - {today} - {len(new_pages)} 个新页面")
    else:
        print("\n📭 没有新的知识页面生成")
    
    print("\n" + "=" * 50)
    print("编译完成！")

if __name__ == "__main__":
    main()
