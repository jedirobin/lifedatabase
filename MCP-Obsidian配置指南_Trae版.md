# MCP-Obsidian 配置指南（Trae版）

> 让Trae通过MCP协议直接操作Obsidian，实现双向链接、标签管理等高级功能

---

## 架构说明

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│    Trae     │ ──MCP──▶│ MCP Server  │ ──REST──▶│  Obsidian   │
│   (AI端)    │         │ (本地运行)   │   API   │  (知识库)   │
└─────────────┘         └─────────────┘         └─────────────┘
```

---

## 第一步：Obsidian端配置

### 1.1 安装Local REST API插件

1. 打开Obsidian
2. 点击左下角 ⚙️ 进入设置
3. 选择 **第三方插件** → **浏览**
4. 搜索 `Local REST API`
5. 找到作者为 **coddingtonbear** 的插件
6. 点击 **安装** → **启用**

### 1.2 获取API Key

1. 安装完成后，进入 **设置 → 第三方插件 → Local REST API**
2. 确保插件状态为 **开启**
3. 找到 **API Key** 字段，点击复制
4. 记住默认端口（通常是 `27124`）

```
你的API Key类似这样：
ca86c3af30488bb26a63a7448235c78ed10ab7465cb3e51a83ff016cfb98c375
```

### 1.3 确认服务运行

在插件设置页面，应该能看到 **Server Running** 状态指示。

---

## 第二步：Trae端配置

### 2.1 打开MCP设置

1. 打开Trae
2. 点击右上角 ⚙️ 进入设置
3. 选择 **MCP** 选项卡

### 2.2 添加MCP服务器

1. 点击 **添加** 按钮
2. 选择 **手动添加**

### 2.3 填写配置信息

将以下JSON粘贴进去（替换你的API Key）：

```json
{
  "mcpServers": {
    "obsidian": {
      "command": "uvx",
      "args": ["mcp-obsidian"],
      "env": {
        "OBSIDIAN_API_KEY": "你的API_KEY",
        "OBSIDIAN_HOST": "127.0.0.1",
        "OBSIDIAN_PORT": "27124",
        "OBSIDIAN_PROTOCOL": "https"
      }
    }
  }
}
```

### 2.4 安装依赖环境

如果提示缺少环境，点击 **安装环境**：
- Trae会自动安装 `uvx` 和 `mcp-obsidian` 包

### 2.5 验证连接

配置成功后，在MCP详情页面应该能看到可用的工具列表。

---

## 第三步：测试MCP功能

### 3.1 测试基本功能

在Trae聊天窗口输入：

```
列出我的Obsidian仓库中的所有文件
```

如果配置正确，Trae会调用 `obsidian_list_files_in_vault` 工具，返回你的笔记列表。

### 3.2 测试双向链接

```
帮我创建一个新笔记，内容包含对 [[项目看板]] 的链接
```

Trae会使用 `obsidian_patch_content` 或相关工具创建带有双向链接的笔记。

### 3.3 测试标签管理

```
给所有包含"AI"的笔记添加 #AI工具 标签
```

---

## MCP-Obsidian 可用工具列表

### 文件操作

| 工具名称 | 功能 |
|---------|------|
| `obsidian_list_files_in_dir` | 列出目录内容 |
| `obsidian_list_files_in_vault` | 列出仓库所有文件 |
| `obsidian_get_file_contents` | 读取单个文件 |
| `obsidian_batch_get_file_contents` | 批量读取文件 |
| `obsidian_patch_content` | 插入内容到笔记 |
| `obsidian_append_content` | 追加内容到笔记末尾 |
| `obsidian_delete_file` | 删除文件/目录 |

### 搜索功能

| 工具名称 | 功能 |
|---------|------|
| `obsidian_simple_search` | 简单关键词搜索 |
| `obsidian_complex_search` | 复杂条件搜索 |

### 周期性笔记

| 工具名称 | 功能 |
|---------|------|
| `obsidian_get_periodic_note` | 获取当前周期笔记 |
| `obsidian_get_recent_periodic_notes` | 获取最近的周期笔记 |

### 动态追踪

| 工具名称 | 功能 |
|---------|------|
| `obsidian_get_recent_changes` | 获取最近修改的文件 |

---

## 第四步（可选）：创建专用智能体

为了更精准地调用MCP，可以创建一个专门的智能体。

### 4.1 创建智能体

1. 在Trae设置中选择 **智能体**
2. 点击 **创建智能体**
3. 名称：`Obsidian助手`

### 4.2 填写提示词

```
你是一个深度集成Obsidian生态的智能代理，通过安全的MCP协议直连用户本地知识库。

核心能力：
- 实时解析Markdown语法与Obsidian特色功能（双向链接、标签系统、Dataview等）
- 理解自然语言查询并转化为精准的文件检索策略
- 掌握知识图谱分析能力，能揭示笔记间的隐性关联
- 熟悉常见知识管理方法论（如Zettelkasten、PARA等）

工作流程：
1. 用户提问时，先搜索相关笔记
2. 分析笔记间的关联关系
3. 自动创建双向链接连接相关笔记
4. 建议标签优化方案
5. 识别知识孤岛并提示用户

输出风格：
- 简洁明了，用表格展示关系
- 主动发现笔记间的隐藏关联
- 建议创建缺失的链接
```

### 4.3 关联MCP

创建智能体时，选择关联 **obsidian** MCP服务器。

---

## 常见问题

### Q1: 连接失败

**检查项**：
1. Obsidian是否正在运行
2. Local REST API插件是否启用
3. API Key是否正确
4. 端口是否被占用（默认27124）

**解决方法**：
```powershell
# 测试端口是否可用
Test-NetConnection -ComputerName 127.0.0.1 -Port 27124
```

### Q2: SSL证书错误

在配置中将 `OBSIDIAN_PROTOCOL` 改为 `http`：
```json
"OBSIDIAN_PROTOCOL": "http"
```

### Q3: 找不到uvx命令

手动安装：
```powershell
# Windows PowerShell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 安装后重启Trae
```

### Q4: 中文乱码

确保Obsidian的Local REST API插件设置中编码为UTF-8。

---

## 使用示例

### 示例1：自动创建链接

```
用户：帮我整理一下关于"AI工具"的所有笔记，并建立关联

Trae会：
1. 搜索所有包含"AI工具"的笔记
2. 创建一个汇总笔记
3. 自动添加 [[AI工具]] 相关的双向链接
4. 建议标签：#AI工具 #效率提升
```

### 示例2：知识图谱分析

```
用户：分析我的项目中笔记的关联情况

Trae会：
1. 扫描所有笔记
2. 分析 [[]] 双向链接
3. 生成关联报告
4. 识别孤立笔记（没有链接的笔记）
5. 建议可以建立的链接
```

### 示例3：批量标签管理

```
用户：给所有提到"KIMI"的笔记添加 #大模型 标签

Trae会：
1. 搜索包含"KIMI"的笔记
2. 检查是否已有标签
3. 批量添加 #大模型 标签
4. 返回修改结果
```

---

## 安全提示

⚠️ **重要**：
- API Key 仅存储在本地，不要分享给他人
- 不要将包含API Key的配置文件上传到公开仓库
- 建议定期更换API Key
- 只在可信的AI工具中使用MCP连接

---

## 配置文件位置参考

| 工具 | 配置文件路径 |
|------|-------------|
| Trae | `%APPDATA%\Trae\mcp-config.json` |
| Claude Desktop | `%APPDATA%\Claude\claude_desktop_config.json` |
| VS Code | 项目根目录 `.vscode/mcp.json` |

---

*文档版本：v1.0*
*创建时间：2026-04-21*
*参考来源：CSDN、GitHub、MCP官方文档*
