#!/usr/bin/env python3
"""
知识库自动编译脚本
基于 Karpathy 架构，自动处理 sources/inbox/ 中的新素材

功能：
1. 扫描 inbox 新文件
2. 调用 MiMo V2.5 Pro API 分析内容
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
import sys

# ============ 配置 ============
KNOWLEDGE_BASE_PATH = Path(__file__).parent.parent
SOURCES_INBOX = KNOWLEDGE_BASE_PATH / "sources" / "inbox"
MEMORY_PATH = KNOWLEDGE_BASE_PATH / "memory"
INDEX_PATH = MEMORY_PATH / "index.md"
PROCESSED_LOG = KNOWLEDGE_BASE_PATH / ".ai" / "processed_files.json"
LOG_FILE = KNOWLEDGE_BASE_PATH / ".ai" / "compile.log"

# MiMo V2.5 Pro API 配置
MIMO_API_URL = "https://token-plan-cn.xiaomimimo.com/v1/chat/completions"
MIMO_API_KEY = "tp-czieisgw65tq93o37k1k7c0pd6c6mz69ectswcurppa3jhrm"
MIMO_MODEL = "mimo-v2.5-pro"

# ============ 日志函数 ============

def log(message, level="INFO"):
    """统一日志输出"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [{level}] {message}"
    print(log_line)
    # 同时写入日志文件
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_line + "\n")

def log_error(message):
    log(message, "ERROR")

def log_success(message):
    log(message, "SUCCESS")

def log_warning(message):
    log(message, "WARNING")

# ============ 工具函数 ============

def get_file_hash(file_path):
    """计算文件哈希，用于判断是否已处理"""
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def load_processed_log():
    """加载已处理文件记录"""
    if PROCESSED_LOG.exists():
        try:
            with open(PROCESSED_LOG, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_processed_log(log_data):
    """保存已处理文件记录"""
    PROCESSED_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(PROCESSED_LOG, 'w', encoding='utf-8') as f:
        json.dump(log_data, f, ensure_ascii=False, indent=2)

def call_mimo_llm(prompt, content):
    """调用 MiMo V2.5 Pro API"""
    headers = {
        "Authorization": f"Bearer {MIMO_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": MIMO_MODEL,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": content}
        ],
        "temperature": 0.3,
        "max_tokens": 2048
    }
    
    try:
        log(f"正在调用 MiMo V2.5 Pro API...")
        response = requests.post(MIMO_API_URL, headers=headers, json=data, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            log_error(f"API 调用失败: {response.status_code} - {response.text[:200]}")
            return None
    except requests.exceptions.Timeout:
        log_error("API 调用超时 (120秒)")
        return None
    except Exception as e:
        log_error(f"API 调用异常: {e}")
        return None

def extract_json_from_response(text):
    """从响应中提取 JSON"""
    if not text:
        return None
    
    # 尝试直接解析
    try:
        return json.loads(text.strip())
    except:
        pass
    
    # 尝试提取代码块
    for marker in ['```json', '```', '```JSON']:
        if marker in text:
            parts = text.split(marker)
            for part in parts[1:]:
                json_text = part.split('```')[0].strip()
                try:
                    return json.loads(json_text)
                except:
                    continue
    
    # 尝试提取 {} 之间的内容
    try:
        start = text.index('{')
        end = text.rindex('}') + 1
        return json.loads(text[start:end])
    except:
        pass
    
    return None

def analyze_content(file_path, file_type):
    """分析内容，提取结构化信息"""
    
    # 读取文件内容
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        log_error(f"读取文件失败: {file_path} - {e}")
        return None
    
    if not content.strip():
        log_warning(f"文件为空: {file_path.name}")
        return None
    
    # 截断过长内容
    max_content_len = 8000
    if len(content) > max_content_len:
        content = content[:max_content_len] + "\n\n[内容已截断]"
        log_warning(f"文件过长，已截断: {file_path.name}")
    
    # 分析提示词
    prompt = """你是一个知识库编译器。请分析以下内容，提取关键信息。

要求：
1. **主要实体**（人物、组织、概念、项目、产品等）- 每个实体需要 name, type, description
2. **关键事实**（重要信息、数据、结论、数字）
3. **核心概念**（需要解释的术语或理论）
4. **标签**（便于分类的关键词）
5. **建议链接**（可能关联到的其他知识页面）

请以严格的 JSON 格式返回，不要包含任何其他文字：
{
    "title": "内容标题（自动生成或从内容提取）",
    "summary": "50字以内的一句话摘要",
    "entities": [
        {"name": "实体名称", "type": "person|project|concept|organization|product|other", "description": "简短描述，一句话"}
    ],
    "facts": ["事实1", "事实2（最多5个）"],
    "concepts": ["概念1", "概念2（最多5个）"],
    "tags": ["标签1", "标签2（最多5个）"],
    "suggested_links": ["可能关联的页面名称"]
}

注意：
- entities 最多提取3个最重要的实体
- facts 只保留最关键的
- 如果无法提取某项，返回空数组 []
- type 只使用指定的类型之一"""
    
    result = call_mimo_llm(prompt, content)
    
    if result:
        analysis = extract_json_from_response(result)
        if analysis:
            log_success(f"分析完成: {analysis.get('title', '未知')}")
            return analysis
        else:
            log_error(f"JSON 解析失败")
    else:
        log_error(f"API 调用失败")
    
    return None

def update_memory_page(entity_info, source_file):
    """更新或创建 memory 页面"""
    entity_type = entity_info.get("type", "concept")
    entity_name = entity_info.get("name", "未知")
    
    if not entity_name or entity_name == "未知":
        return None
    
    # 确定目标目录
    type_to_dir = {
        "person": "people",
        "project": "projects",
        "concept": "concepts",
        "organization": "accounts",
        "product": "projects",
        "account": "accounts",
        "other": "concepts"
    }
    target_dir = MEMORY_PATH / type_to_dir.get(entity_type, "concepts")
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建文件名（安全处理）
    safe_name = "".join(c for c in entity_name if c.isalnum() or c in ('-', '_', ' '))
    safe_name = safe_name.strip()[:50]  # 限制长度
    file_path = target_dir / f"{safe_name}.md"
    
    # 生成页面内容
    today = datetime.now().strftime("%Y-%m-%d")
    
    if file_path.exists():
        # 追加到已有页面
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                existing = f.read()
            
            # 检查是否已包含此来源
            if source_file.name in existing:
                log_warning(f"页面已包含此来源，跳过: {file_path.name}")
                return file_path
            
            # 追加到 Timeline
            new_entry = f"""**{today}** | 知识更新 — 来源: {source_file.name}
- {entity_info.get('description', '')}

"""
            if "## Timeline" in existing:
                updated = existing.replace("## Timeline", f"## Timeline\n{new_entry}")
            else:
                updated = existing + f"\n\n---\n\n## Timeline\n{new_entry}"
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated)
            
            log_success(f"更新页面: {file_path.name}")
        except Exception as e:
            log_error(f"更新页面失败: {file_path.name} - {e}")
            return None
    else:
        # 创建新页面
        page_content = f"""---
title: {entity_name}
type: {entity_type}
tags: [{', '.join(entity_info.get('tags', [])[:5])}]
created: {today}
updated: {today}
source: {source_file.name}
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
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(page_content)
            log_success(f"创建页面: {file_path.name}")
        except Exception as e:
            log_error(f"创建页面失败: {file_path.name} - {e}")
            return None
    
    return file_path

def update_index(new_pages):
    """更新索引文件"""
    if not new_pages:
        return
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 读取现有索引
    if INDEX_PATH.exists():
        try:
            with open(INDEX_PATH, 'r', encoding='utf-8') as f:
                index_content = f.read()
        except:
            index_content = ""
    else:
        index_content = ""
    
    # 检查是否已有新增条目部分
    if "## 新增条目" in index_content:
        log("索引中已有新增条目部分，跳过重复更新")
        return
    
    # 添加新条目
    new_entries = f"\n---\n\n## 新增条目 ({today})\n"
    for page in new_pages:
        if page and page.exists():
            rel_path = page.relative_to(MEMORY_PATH)
            category = page.parent.name
            new_entries += f"- [[{rel_path.stem}]] - {category}\n"
    
    # 更新最后更新时间
    index_content = index_content.replace(
        "> 最后更新：", 
        f"> 最后更新：{today}"
    )
    
    # 如果没有找到最后更新时间，就在末尾添加
    if "> 最后更新：" not in index_content:
        index_content = index_content.strip() + f"\n\n> 最后更新：{today}\n"
    
    # 追加新条目
    index_content += new_entries
    
    try:
        with open(INDEX_PATH, 'w', encoding='utf-8') as f:
            f.write(index_content)
        log_success(f"索引已更新")
    except Exception as e:
        log_error(f"索引更新失败: {e}")

def git_commit_push(message):
    """Git 提交并推送"""
    try:
        os.chdir(KNOWLEDGE_BASE_PATH)
        
        # 检查是否有更改
        result = subprocess.run(["git", "status", "--porcelain"], 
                              capture_output=True, text=True)
        if not result.stdout.strip():
            log("没有更改需要提交")
            return True
        
        # 配置 git 用户（如果需要）
        subprocess.run(["git", "config", "user.name", "NEKO"], check=False)
        subprocess.run(["git", "config", "user.email", "neko@agent-world.local"], check=False)
        
        subprocess.run(["git", "add", "-A"], check=True)
        result = subprocess.run(["git", "commit", "-m", message], 
                              capture_output=True, text=True)
        
        if result.returncode != 0:
            if "nothing to commit" in result.stderr:
                log("没有更改需要提交")
                return True
            log_error(f"Git 提交失败: {result.stderr}")
            return False
        
        # 尝试推送
        result = subprocess.run(["git", "push"], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            log_success(f"Git 推送成功")
            return True
        else:
            log_warning(f"Git 推送失败 (可能没有网络权限): {result.stderr[:200]}")
            return True  # 不因为推送失败而报错
        
    except subprocess.TimeoutExpired:
        log_warning("Git 推送超时")
        return True
    except Exception as e:
        log_error(f"Git 操作异常: {e}")
        return False

# ============ 主流程 ============

def main():
    """主流程"""
    print("\n" + "=" * 60)
    print("🔄 知识库自动编译 - Karpathy 架构")
    print(f"⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60 + "\n")
    
    # 确保必要目录存在
    SOURCES_INBOX.mkdir(parents=True, exist_ok=True)
    MEMORY_PATH.mkdir(parents=True, exist_ok=True)
    
    # 加载已处理记录
    processed = load_processed_log()
    new_pages = []
    errors = []
    
    # 扫描 inbox
    try:
        files = list(SOURCES_INBOX.glob("*"))
        files = [f for f in files if f.is_file() and not f.name.startswith('.')]
    except Exception as e:
        log_error(f"扫描 inbox 失败: {e}")
        sys.exit(1)
    
    if not files:
        log("📭 inbox 为空，没有新文件需要处理")
        print("\n" + "=" * 60)
        print("✅ 编译完成！")
        print("=" * 60 + "\n")
        return
    
    log(f"📂 发现 {len(files)} 个文件待处理")
    
    # 处理每个文件
    for file_path in files:
        print(f"\n{'─' * 40}")
        file_hash = get_file_hash(file_path)
        
        # 检查是否已处理
        if file_path.name in processed and processed[file_path.name] == file_hash:
            log(f"⏭️  跳过已处理: {file_path.name}")
            continue
        
        log(f"📄 处理: {file_path.name}")
        
        # 分析内容
        file_type = file_path.suffix.lstrip('.')
        analysis = analyze_content(file_path, file_type)
        
        if not analysis:
            log_warning(f"⚠️  分析失败，记录错误: {file_path.name}")
            errors.append(file_path.name)
            # 仍然标记为已处理，避免重复尝试
            processed[file_path.name] = file_hash
            save_processed_log(processed)
            continue
        
        log(f"   标题: {analysis.get('title', '未知')}")
        log(f"   摘要: {analysis.get('summary', '')[:50]}...")
        log(f"   实体: {len(analysis.get('entities', []))} 个")
        
        # 更新 memory 页面
        for entity in analysis.get('entities', []):
            page_path = update_memory_page(entity, file_path)
            if page_path:
                new_pages.append(page_path)
        
        # 记录已处理
        processed[file_path.name] = file_hash
        save_processed_log(processed)
    
    # 更新索引
    if new_pages:
        update_index(new_pages)
        log_success(f"📚 索引已更新，新增 {len(new_pages)} 个页面")
        
        # Git 提交
        today = datetime.now().strftime("%Y-%m-%d")
        git_message = f"📝 知识库自动编译 - {today} - {len(new_pages)} 个新页面"
        git_commit_push(git_message)
    else:
        if not errors:
            log("📭 没有新的知识页面生成")
        else:
            log_warning(f"⚠️  {len(errors)} 个文件处理失败")
    
    print("\n" + "=" * 60)
    print("✅ 编译完成！")
    if errors:
        print(f"⚠️  {len(errors)} 个文件处理失败")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()
