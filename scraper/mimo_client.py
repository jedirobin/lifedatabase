#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MiMo大模型集成模块
基于 Xiaomi MiMo Token Plan API
"""
import os
import json
import requests
from typing import List, Dict, Any, Optional
from pathlib import Path
from loguru import logger

from config import MIMO_CONFIG


class MiMoClient:
    def __init__(self, api_key: str = None, base_url: str = None, model: str = "mimo-v2.5-pro"):
        self.api_key = api_key or MIMO_CONFIG.get("api_key") or os.getenv("MIMO_API_KEY", "")
        self.base_url = base_url or MIMO_CONFIG.get("base_url") or "https://token-plan-cn.xiaomimimo.com/v1"
        self.model = model or MIMO_CONFIG.get("model") or "mimo-v2.5-pro"
        
        if not self.api_key:
            logger.warning("MiMo API Key未配置，请检查环境变量 MIMO_API_KEY")
    
    def chat(self, messages: List[Dict[str, str]], system_prompt: str = None, max_tokens: int = 4096) -> Optional[str]:
        """发送对话请求"""
        if not self.api_key:
            logger.error("MiMo API Key未设置，无法发送请求")
            return None
        
        headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "max_completion_tokens": max_tokens
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                logger.error(f"MiMo API请求失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"MiMo API异常: {e}")
            return None
    
    def analyze_content(self, content: str, task: str = "分析") -> Optional[str]:
        """分析内容"""
        messages = [
            {"role": "user", "content": f"{task}\n\n{content}"}
        ]
        return self.chat(messages)
    
    def extract_insights(self, content: str) -> Optional[str]:
        """提取洞察"""
        system_prompt = """你是一个专业的内容分析师。请从提供的内容中提取：
1. 核心观点
2. 关键数据
3. 主要结论
4. 行动建议

以结构化的方式输出。"""
        messages = [{"role": "user", "content": content}]
        return self.chat(messages, system_prompt=system_prompt)
    
    def generate_summary(self, content: str, max_length: int = 500) -> Optional[str]:
        """生成摘要"""
        messages = [
            {"role": "user", "content": f"请用不超过{max_length}字概括以下内容的要点：\n\n{content}"}
        ]
        return self.chat(messages)
    
    def batch_analyze(self, contents: List[str], task: str = "分析") -> List[Optional[str]]:
        """批量分析"""
        results = []
        for content in contents:
            result = self.analyze_content(content, task)
            results.append(result)
        return results


class MiMoKnowledgeBase:
    """MiMo知识库集成"""
    
    def __init__(self):
        self.client = MiMoClient()
        self.root_dir = Path(__file__).parent.parent.parent
    
    def compile_article(self, article_path: Path) -> Optional[str]:
        """编译文章为知识"""
        if not article_path.exists():
            logger.error(f"文章不存在: {article_path}")
            return None
        
        content = article_path.read_text(encoding="utf-8")
        
        system_prompt = """你是一个专业的知识工程师。请将文章内容编译成结构化的知识条目，
包含：标题、核心概念、关键知识点、相关人物/项目、应用场景。
输出格式为Markdown。"""
        
        messages = [{"role": "user", "content": content}]
        return self.client.chat(messages, system_prompt=system_prompt)
    
    def analyze_social_data(self, platform: str, data: List[Dict]) -> Optional[str]:
        """分析社媒数据"""
        system_prompt = f"""你是一个专业的社媒运营分析师。请分析{platform}的数据，
提取：爆款规律、内容特征、受众偏好、创作建议。
数据为JSON格式。"""
        
        content = json.dumps(data, ensure_ascii=False)
        messages = [{"role": "user", "content": content}]
        return self.client.chat(messages, system_prompt=system_prompt)
    
    def generate_script(self, brief: str, style: str = "知识分享") -> Optional[str]:
        """生成脚本"""
        system_prompt = f"""你是一个专业的短视频脚本作家。请根据brief生成一个{style}风格的脚本。
包含：开场、主体、结尾，时长控制在1-3分钟。
输出格式为Markdown，包含分镜和台词。"""
        
        messages = [{"role": "user", "content": brief}]
        return self.client.chat(messages, system_prompt=system_prompt)


def test_connection():
    """测试MiMo连接"""
    client = MiMoClient()
    
    if not client.api_key:
        print("❌ API Key未配置")
        return False
    
    print("🔄 正在测试MiMo连接...")
    print(f"   API: {client.base_url}")
    print(f"   Model: {client.model}")
    
    response = client.chat([
        {"role": "user", "content": "请用一句话介绍自己"}
    ])
    
    if response:
        print(f"✅ MiMo连接成功！\n回复: {response}")
        return True
    else:
        print("❌ MiMo连接失败")
        return False


if __name__ == "__main__":
    test_connection()
