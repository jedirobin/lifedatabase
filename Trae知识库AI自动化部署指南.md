# Trae实现Karpathy知识库AI自动化流程

> 本文档指导如何在Trae上实现Karpathy风格的知识库自动化，实现"人类扔素材 → AI编译知识 → 产出内容"的闭环

---

## 一、整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        三端协作架构                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐      │
│   │   Trae端    │     │  Obsidian端 │     │   Coze端    │      │
│   │  (本地AI)   │     │  (知识库)   │     │  (云端调度) │      │
│   └──────┬──────┘     └──────┬──────┘     └──────┬──────┘      │
│          │                   │                   │              │
│          │  直接操作本地文件   │                   │              │
│          ├──────────────────►│                   │              │
│          │                   │                   │              │
│          │                   │   Git同步         │              │
│          │                   │◄─────────────────►│              │
│          │                   │                   │              │
│          │   定时任务/远程触发  │                   │              │
│          │◄──────────────────────────────────────┤              │
│          │                   │                   │              │
└──────────┴───────────────────┴───────────────────┴──────────────┘

数据流向：
1. 人类 → sources/（扔素材）
2. Trae AI → memory/（编译知识）
3. Trae AI → outputs/（产出内容）
4. Git → GitHub → Obsidian（查看）
5. Coze → 定时任务 → 触发Trae执行
```

### 核心原则（Karpathy理念）

1. **LLM是唯一作者**：memory/目录由AI维护，人类只往sources/扔东西
2. **知识流动单向**：sources → memory → outputs
3. **无需Git版本管理**：LLM自己维护结构，Git只是同步工具
4. **Obsidian只是浏览器**：查看知识库，不直接编辑memory/

---

## 二、目录结构

```
lifedatabase/
├── sources/                    # Layer 1: 原始输入（人类操作）
│   ├── articles/              # 文章原文（粘贴或剪藏）
│   ├── videos/                # 视频字幕/文稿
│   ├── podcasts/              # 播客转录
│   ├── pdfs/                  # PDF文档
│   ├── ppts/                  # PPT源文件
│   ├── social/                # 社媒数据
│   │   ├── douyin/
│   │   ├── bilibili/
│   │   └── xiaohongshu/
│   └── inbox/                 # 待处理收件箱（人类扔东西的地方）
│
├── memory/                     # Layer 2: 编译后的知识（AI维护）
│   ├── context/               # 背景知识
│   ├── accounts/              # 账号档案
│   ├── projects/              # 项目档案
│   ├── people/                # 人物档案
│   ├── concepts/              # 概念解释
│   ├── insights/              # 洞察总结
│   ├── index.md               # 全局索引
│   └── schema.md              # 结构定义
│
├── outputs/                    # Layer 3: 产出物（AI生成）
│   ├── ppts/                  # 生成的PPT
│   ├── reports/               # 分析报告
│   ├── scripts/               # 脚本内容
│   └── plans/                 # 规划文档
│
├── templates/                  # 模板库（AI参考）
│
├── .ai/                        # AI配置目录
│   ├── CLAUDE.md              # Claude/DeepSeek提示词
│   ├── TASKS.md               # 任务队列
│   └── config.json            # 配置文件
│
└── 创意工厂/                    # 创意生产系统
    ├── 灵感库/
    ├── 剧本/
    └── 作品/
```

---

## 三、Trae端配置

### 3.1 安装Trae

1. 下载Trae：https://trae.ai
2. 安装时选择"连接本地模型"或"使用API"
3. 推荐配置：
   - 本地模型：Ollama + Qwen2.5-7B（免费、中文好）
   - 云端API：DeepSeek / KIMI / GLM（已配置）

### 3.2 配置AI模型

**方式一：使用本地模型（推荐）**

```bash
# 1. 安装Ollama
# Windows: 下载 https://ollama.com/download

# 2. 拉取模型
ollama pull qwen2.5:7b

# 3. 在Trae中配置
# 设置 → 模型 → 选择Ollama → 地址 http://localhost:11434
```

**方式二：使用云端API**

在Trae中配置：
```
模型: DeepSeek Chat
API地址: https://api.deepseek.com
API Key: sk-xxxxxxxx（从 ~/.ai_keys/deepseek.txt 获取）
```

### 3.3 打开知识库项目

```bash
# 在Trae中打开项目
File → Open Folder → 选择 lifedatabase 目录
```

### 3.4 配置AI上下文

Trae会自动读取 `.ai/CLAUDE.md` 作为AI的系统提示词。

---

## 四、Obsidian端配置

### 4.1 安装必要插件

1. **Templater**：模板系统
2. **Dataview**：数据查询
3. **Git**：版本同步（可选）
4. **Smart Connections**：AI检索（可选）

### 4.2 配置Git同步

```bash
# 在Obsidian仓库目录打开终端
cd E:\obsidianbase\lifedatabase

# 拉取最新内容
git pull origin main

# 设置自动同步（可选）
# 安装Obsidian Git插件，配置自动pull/push
```

### 4.3 使用规则

| 目录 | 人类操作 | AI操作 |
|------|---------|--------|
| `sources/` | ✅ 可编辑 | ❌ 只读 |
| `memory/` | ❌ 只读 | ✅ 可编辑 |
| `outputs/` | ❌ 只读 | ✅ 可编辑 |
| `创意工厂/灵感库/` | ✅ 可编辑 | ✅ 可读取 |

**人类只需要做两件事**：
1. 往 `sources/inbox/` 扔素材
2. 在Obsidian里查看 `memory/` 和 `outputs/`

---

## 五、Coze端配置

### 5.1 已有配置

- 日程系统：日报/周报/月报
- 创意工厂：每日脑洞推送
- Git同步：自动推送到GitHub

### 5.2 新增任务（可选）

如果需要Coze触发Trae执行任务：

1. **Webhook触发**：Coze发送HTTP请求到本地服务器
2. **GitHub Actions**：Coze推送触发词到仓库，Trae监听执行
3. **手动触发**：Coze生成任务文件，Trae定期扫描执行

### 5.3 协作流程

```
Coze日程触发 → 生成任务文件 → 推送GitHub → Trae检测执行 → 结果回推
```

---

## 六、核心工作流程

### 6.1 素材导入流程（Ingest）

**人类操作**：
1. 把素材扔到 `sources/inbox/`
   - 文章：粘贴到 `inbox/article_xxx.md`
   - 视频：字幕文件放到 `inbox/video_xxx.txt`
   - PDF：复制到 `inbox/xxx.pdf`

**Trae AI操作**：
```markdown
任务：处理 inbox 中的新素材

步骤：
1. 扫描 sources/inbox/ 目录
2. 识别素材类型（文章/视频/播客/PDF）
3. 提取关键信息：
   - 标题、作者、日期
   - 核心观点
   - 关键人物/概念
4. 移动到对应目录：sources/articles/、sources/videos/等
5. 创建或更新 memory/ 中的相关页面
6. 更新 memory/index.md 索引
7. 清空 inbox/
```

### 6.2 知识查询流程（Query）

**人类操作**：
在Trae中输入问题，例如：
```
"帮我查一下B站AI工具类账号的爆款特征"
```

**Trae AI操作**：
```markdown
步骤：
1. 读取 memory/index.md 找到相关页面
2. 搜索 memory/accounts/ 中的账号档案
3. 读取 memory/insights/ 中的洞察
4. 综合信息生成回答
5. 如果信息不足，提示需要补充的素材
```

### 6.3 内容生成流程（Generate）

**人类操作**：
```
"根据这个账号的分析，帮我写一个脚本"
```

**Trae AI操作**：
```markdown
步骤：
1. 读取相关 memory/ 页面
2. 读取 templates/ 中的脚本模板
3. 生成脚本内容
4. 保存到 outputs/scripts/xxx.md
5. 如果需要评审，调用评审API
```

---

## 七、Trae执行脚本

### 7.1 素材处理脚本

保存为 `.ai/scripts/ingest.py`：

```python
#!/usr/bin/env python3
"""
素材处理脚本 - 自动导入inbox中的新素材
"""
import os
import shutil
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent.parent
INBOX_DIR = BASE_DIR / "sources" / "inbox"
SOURCES_DIR = BASE_DIR / "sources"

def get_file_type(filename: str) -> str:
    """根据扩展名判断文件类型"""
    ext = Path(filename).suffix.lower()
    type_map = {
        '.pdf': 'pdfs',
        '.ppt': 'ppts', '.pptx': 'ppts',
        '.mp3': 'podcasts', '.wav': 'podcasts',
        '.mp4': 'videos', '.mkv': 'videos',
        '.md': 'articles', '.txt': 'articles',
    }
    return type_map.get(ext, 'articles')

def process_inbox():
    """处理inbox中的所有文件"""
    if not INBOX_DIR.exists():
        INBOX_DIR.mkdir(parents=True)
        return
    
    for file in INBOX_DIR.iterdir():
        if file.is_file():
            file_type = get_file_type(file.name)
            target_dir = SOURCES_DIR / file_type
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # 添加日期前缀
            date_prefix = datetime.now().strftime("%Y%m%d")
            new_name = f"{date_prefix}_{file.name}"
            target_path = target_dir / new_name
            
            shutil.move(str(file), str(target_path))
            print(f"✅ 移动: {file.name} → {target_dir.name}/{new_name}")

if __name__ == "__main__":
    process_inbox()
```

### 7.2 知识编译脚本

保存为 `.ai/scripts/compile.py`：

```python
#!/usr/bin/env python3
"""
知识编译脚本 - 从sources提取知识到memory
"""
import os
import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent.parent
SOURCES_DIR = BASE_DIR / "sources"
MEMORY_DIR = BASE_DIR / "memory"

def extract_metadata(content: str, filepath: Path) -> dict:
    """从内容中提取元数据"""
    lines = content.split('\n')
    title = lines[0].replace('#', '').strip() if lines else filepath.stem
    
    return {
        'title': title,
        'source': str(filepath.relative_to(BASE_DIR)),
        'date': datetime.now().strftime("%Y-%m-%d"),
        'word_count': len(content)
    }

def update_index(new_entry: dict):
    """更新索引文件"""
    index_path = MEMORY_DIR / "index.md"
    
    if index_path.exists():
        content = index_path.read_text(encoding='utf-8')
    else:
        content = "# 知识库索引\n\n"
    
    # 添加新条目
    new_line = f"- [[{new_entry['title']}]] - {new_entry['date']}\n"
    if new_line not in content:
        content += new_line
        index_path.write_text(content, encoding='utf-8')
        print(f"✅ 更新索引: {new_entry['title']}")

def compile_sources():
    """编译所有sources"""
    for source_type in ['articles', 'videos', 'podcasts']:
        type_dir = SOURCES_DIR / source_type
        if not type_dir.exists():
            continue
        
        for file in type_dir.glob("*.md"):
            try:
                content = file.read_text(encoding='utf-8')
                metadata = extract_metadata(content, file)
                update_index(metadata)
            except Exception as e:
                print(f"⚠️ 处理失败: {file.name} - {e}")

if __name__ == "__main__":
    compile_sources()
```

---

## 八、快速开始

### 8.1 第一次使用

```bash
# 1. 克隆仓库
git clone git@github.com:jedirobin/lifedatabase.git
cd lifedatabase

# 2. 创建必要目录
mkdir -p sources/inbox memory outputs templates .ai/scripts

# 3. 在Trae中打开项目
# File → Open Folder → lifedatabase

# 4. 测试：往inbox扔一个文件
echo "# 测试文章\n\n这是一篇测试文章的内容。" > sources/inbox/test_article.md

# 5. 让Trae执行
# 在Trae聊天窗口输入：
# "请执行素材处理脚本，处理inbox中的文件"
```

### 8.2 日常使用

**每天**：
1. 把收集的素材扔到 `sources/inbox/`
2. 打开Trae，说"处理今天的素材"
3. 在Obsidian中查看更新后的知识

**每周**：
1. 在Trae中说"生成本周知识总结"
2. 检查 `outputs/reports/` 中的报告

---

## 九、故障排除

### Q1: Trae无法读取文件

```bash
# 检查文件权限
ls -la lifedatabase/

# 如果权限不足
chmod -R 755 lifedatabase/
```

### Q2: Git同步冲突

```bash
# 强制使用远程版本
git fetch origin
git reset --hard origin/main

# 或者保留本地版本
git stash
git pull origin main
git stash pop
```

### Q3: AI模型响应慢

- 本地模型：检查Ollama是否运行 `ollama ps`
- 云端API：检查网络和API Key有效性

---

## 十、进阶配置

### 10.1 自动化脚本（Windows任务计划）

```powershell
# 创建定时任务：每天晚上处理素材
$trigger = New-ScheduledTaskTrigger -Daily -At 8pm
$action = New-ScheduledTaskAction -Execute "python" -Argument "E:\obsidianbase\lifedatabase\.ai\scripts\ingest.py"
Register-ScheduledTask -TaskName "知识库素材处理" -Trigger $trigger -Action $action
```

### 10.2 与Coze联动

在 `.ai/` 目录创建 `webhook_server.py`：

```python
from flask import Flask, request
import subprocess

app = Flask(__name__)

@app.route('/trigger', methods=['POST'])
def trigger_task():
    task = request.json.get('task')
    if task == 'ingest':
        subprocess.run(['python', '.ai/scripts/ingest.py'])
    return {'status': 'ok'}

if __name__ == '__main__':
    app.run(port=5000)
```

---

## 附录：文件命名规范

| 类型 | 格式 | 示例 |
|------|------|------|
| 文章 | `YYYYMMDD_标题.md` | `20260421_AI工具测评指南.md` |
| 视频 | `YYYYMMDD_平台_标题.txt` | `20260421_bilibili_爆款分析.txt` |
| PDF | `YYYYMMDD_文档名.pdf` | `20260421_产品说明书.pdf` |
| 账号档案 | `平台_账号名.md` | `bilibili_科技美学.md` |
| 项目档案 | `项目名称.md` | `社媒运营项目.md` |
| 洞察 | `YYYYMMDD_主题.md` | `20260421_爆款特征分析.md` |

---

*文档版本：v1.0*
*创建时间：2026-04-21*
*维护者：NEKO*
