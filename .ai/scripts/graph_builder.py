#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Karpathy Wiki 知识图谱构建器
功能：
  1. 实体识别（概念、人物、账号、洞察）
  2. 自动双向链接 [[页面名]]
  3. 原子化节点生成
  4. 图谱索引更新
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import re
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

SCRIPT_DIR = Path(__file__).parent
BASE_DIR = SCRIPT_DIR.parent.parent
MEMORY_DIR = BASE_DIR / "memory"
SOURCES_DIR = BASE_DIR / "sources"

ENTITY_TYPES = {
    'concept': {'dir': 'concepts', 'prefix': 'C-'},
    'person': {'dir': 'people', 'prefix': 'P-'},
    'account': {'dir': 'accounts', 'prefix': 'A-'},
    'insight': {'dir': 'insights', 'prefix': 'I-'},
    'project': {'dir': 'projects', 'prefix': 'Prj-'},
}

# 预定义实体词典（可不断扩展）
ENTITY_DICT = {
    'concepts': [
        '互动率', '完播率', '爆款', '钩子', '黄金3秒', '评论区',
        '弹幕', '标签', '分区', '算法', '流量池', '冷启动',
        '完播率', '点赞率', '转化率', '用户画像', '内容定位'
    ],
    'people': [
        '万灵缝合厂', '钟钟AIZz', '朱一旦', '伊丽莎白鼠', '小可儿',
        '张三', '罗翔', '半佛仙人', '巫师财经'
    ],
    'accounts': [
        '钟钟AIZz', '万灵缝合厂', '朱一旦的枯燥生活'
    ]
}

class KnowledgeGraph:
    def __init__(self):
        self.nodes = {}
        self.edges = defaultdict(list)
        self.entity_index = self._build_entity_index()
        self._init_dirs()
    
    def _init_dirs(self):
        for etype in ENTITY_TYPES.values():
            d = MEMORY_DIR / etype['dir']
            d.mkdir(exist_ok=True)
    
    def _build_entity_index(self):
        """扫描现有节点，建立实体索引"""
        index = {}
        for etype, info in ENTITY_TYPES.items():
            node_dir = MEMORY_DIR / info['dir']
            if node_dir.exists():
                for f in node_dir.glob("*.md"):
                    clean_name = f.stem.replace(info['prefix'], '')
                    index[clean_name] = {
                        'file': f,
                        'type': etype,
                        'full_name': f.stem
                    }
                    for alias in self._extract_aliases(f.read_text(encoding='utf-8')):
                        index[alias] = {
                            'file': f,
                            'type': etype,
                            'full_name': f.stem
                        }
        return index
    
    def _extract_aliases(self, content: str) -> list:
        """从页面YAML中提取别名"""
        m = re.search(r'aliases:\s*\[([^\]]+)\]', content)
        if m:
            return [a.strip().strip('"').strip("'") for a in m.group(1).split(',')]
        return []
    
    def _link_entities(self, text: str) -> str:
        """自动识别并链接已知实体"""
        linked_text = text
        linked = set()
        
        for entity_name, info in self.entity_index.items():
            if len(entity_name) < 2:
                continue
            pattern = r'(?<!\[)(' + re.escape(entity_name) + r')(?!\])'
            if re.search(pattern, linked_text) and entity_name not in linked:
                linked_text = re.sub(
                    pattern,
                    f'[[{info["full_name"]}|{entity_name}]]',
                    linked_text
                )
                linked.add(entity_name)
        
        return linked_text
    
    def _extract_frontmatter(self, content: str) -> dict:
        """提取YAML frontmatter"""
        m = re.match(r'---\n(.*?)\n---', content, re.DOTALL)
        if m:
            fm = m.group(1)
            result = {}
            for line in fm.split('\n'):
                if ':' in line:
                    k, v = line.split(':', 1)
                    result[k.strip()] = v.strip()
            return result
        return {}
    
    def create_node(self, node_type: str, title: str, content: str, **kwargs) -> Path:
        """创建原子化知识节点"""
        info = ENTITY_TYPES[node_type]
        clean_title = re.sub(r'[\\/*?"<>|]', '', title).strip()
        filename = f"{info['prefix']}{clean_title}.md"
        filepath = MEMORY_DIR / info['dir'] / filename
        
        tags = kwargs.get('tags', [])
        aliases = kwargs.get('aliases', [])
        confidence = kwargs.get('confidence', 0.5)
        
        linked_content = self._link_entities(content)
        
        frontmatter = [
            '---',
            f'type: {node_type}',
            f'tags: {json.dumps(tags, ensure_ascii=False)}'
        ]
        if aliases:
            frontmatter.append(f'aliases: {json.dumps(aliases, ensure_ascii=False)}')
        if node_type == 'insight':
            frontmatter.append(f'confidence: {confidence}')
        frontmatter.extend([
            f'created: {datetime.now().strftime("%Y-%m-%d")}',
            '---\n'
        ])
        
        full_content = '\n'.join(frontmatter) + f"# {clean_title}\n\n{linked_content}\n"
        
        if filepath.exists():
            old_content = filepath.read_text(encoding='utf-8')
            if linked_content not in old_content:
                full_content = old_content + "\n---\n" + f"\n## 补充 - {datetime.now().strftime('%Y-%m-%d')}\n\n" + linked_content
                filepath.write_text(full_content, encoding='utf-8')
                print(f"📝 更新: {filename}")
            else:
                print(f"⏭️  跳过: {filename} (无新内容)")
        else:
            filepath.write_text(full_content, encoding='utf-8')
            print(f"✨ 新建: {filename}")
        
        self.entity_index[clean_title] = {
            'file': filepath,
            'type': node_type,
            'full_name': f"{info['prefix']}{clean_title}"
        }
        
        return filepath
    
    def extract_insights_from_text(self, text: str, source: str = ""):
        """从文本中提取洞察（规则版，后续接入LLM）"""
        insights = []
        
        patterns = [
            (r'(爆款|播放量|点赞).*公式', '爆款公式'),
            (r'(?i)(er|互动率|engagement rate)', '互动率定义'),
            (r'前.*秒.*(钩子|冲突|吸引)', '开头法则'),
            (r'评论区.*(重要|影响|作用)', '评论区价值'),
            (r'弹幕.*效果', '弹幕效应'),
        ]
        
        for pattern, name_hint in patterns:
            for m in re.finditer(pattern, text):
                start = max(0, m.start() - 100)
                end = min(len(text), m.end() + 200)
                context = text[start:end]
                
                if source:
                    context += f"\n\n**来源**: [[{source}]]"
                
                insights.append({
                    'title': f"关于{name_hint}的发现",
                    'content': context,
                    'tags': ['自动提取', name_hint],
                    'confidence': 0.6
                })
        
        return insights
    
    def update_graph_index(self):
        """更新图谱主索引"""
        stats = defaultdict(int)
        all_nodes = []
        
        for etype, info in ENTITY_TYPES.items():
            node_dir = MEMORY_DIR / info['dir']
            if node_dir.exists():
                for f in node_dir.glob("*.md"):
                    stats[etype] += 1
                    all_nodes.append({
                        'name': f.stem,
                        'type': etype,
                        'path': f.relative_to(BASE_DIR),
                        'mtime': f.stat().st_mtime
                    })
        
        all_nodes.sort(key=lambda x: x['mtime'], reverse=True)
        
        index_content = f"""# 🔭 知识图谱索引

> Karpathy Wiki v2.0  
> 最后更新：{datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## 📊 图谱概览

| 节点类型 | 数量 |
|---------|------|
| 🧩 概念 (Concept) | {stats['concept']} |
| 👤 人物 (Person) | {stats['person']} |
| 📺 账号 (Account) | {stats['account']} |
| 💡 洞察 (Insight) | {stats['insight']} |
| 📋 项目 (Project) | {stats['project']} |
| **总计** | **{sum(stats.values())}** |

---

## ✨ 最近更新节点

"""
        
        for node in all_nodes[:15]:
            type_icon = {
                'concept': '🧩',
                'person': '👤',
                'account': '📺',
                'insight': '💡',
                'project': '📋'
            }.get(node['type'], '📄')
            mtime_str = datetime.fromtimestamp(node['mtime']).strftime('%Y-%m-%d')
            index_content += f"- {type_icon} [[{node['name']}]] - {mtime_str}\n"
        
        index_content += f"""

---

## 🚀 图谱探索提示

1. **点击任意 [[链接]]** 进入节点
2. **查看 Obsidian 反向链接** - 发现关联知识
3. **打开图谱视图** - Command/Ctrl + G
4. **Trae 中提问** - "帮我分析一下知识图谱中的关联"

---

*"Knowledge is a graph, not a tree"* — Karpathy
"""
        
        index_path = MEMORY_DIR / "index.md"
        index_path.write_text(index_content, encoding='utf-8')
        print(f"\n✅ 更新图谱索引: {sum(stats.values())} 个节点")
        
        return stats
    
    def build_from_sources(self):
        """从 sources 构建知识图谱"""
        line = "=" * 60
        print(f"\n{line}")
        print("  Karpathy Wiki 知识图谱构建器")
        print(f"{line}\n")
        
        print(f"已加载 {len(self.entity_index)} 个已有的实体索引\n")
        
        source_files = []
        for ext in ['*.md', '*.txt']:
            source_files.extend(SOURCES_DIR.rglob(ext))
        
        print(f"扫描到 {len(source_files)} 个源文件\n")
        
        total_insights = 0
        for f in source_files:
            try:
                content = f.read_text(encoding='utf-8')
                insights = self.extract_insights_from_text(content, f.stem)
                
                for insight in insights:
                    self.create_node(
                        'insight',
                        insight['title'],
                        insight['content'],
                        tags=insight['tags'],
                        confidence=insight['confidence']
                    )
                    total_insights += 1
            except Exception as e:
                print(f"处理失败 {f.name}: {e}")
        
        print(f"\n{'-' * 60}")
        print(f"提取了 {total_insights} 个新洞察\n")
        
        stats = self.update_graph_index()
        
        print(f"\n{line}")
        print("   知识图谱构建完成！")
        print(f"{line}\n")
        print("在 Obsidian 中探索：")
        print("   1. 打开 memory/index.md 浏览索引")
        print("   2. 按 Cmd/Ctrl + G 查看图谱视图")
        print("   3. 点击任意 [[链接]] 漫游知识网络\n")


def main():
    kg = KnowledgeGraph()
    kg.build_from_sources()


if __name__ == "__main__":
    main()
