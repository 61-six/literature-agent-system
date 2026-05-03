"""
分类标注Agent - 负责文档自动分类和关键词提取
"""
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from core.llm_client import llm_client
from config.settings import TECH_CATEGORIES, MAX_KEYWORDS


class ClassifierAgent:
    def __init__(self):
        self.name = "ClassifierAgent"
        self.description = "分类标注Agent，负责文档自动分类和关键词提取"
        self.categories = TECH_CATEGORIES
        self.max_keywords = MAX_KEYWORDS

    def process(self, preprocessed_data: Dict[str, Any]) -> Dict[str, Any]:
        result = {
            "agent": self.name,
            "status": "pending",
            "input_doc_id": preprocessed_data.get("doc_id", ""),
            "output": {}
        }

        try:
            content = preprocessed_data.get("output", {}).get("content", "")
            metadata = preprocessed_data.get("output", {}).get("metadata", {})

            if not content:
                result["status"] = "failed"
                result["error"] = "没有内容可以分类"
                return result

            category = self._classify_document(content, metadata)
            keywords = self._extract_keywords(content, metadata)
            tech_research_direction = self._analyze_research_direction(content, category)

            result["status"] = "completed"
            result["output"] = {
                "category": category,
                "keywords": keywords,
                "tech_research_direction": tech_research_direction,
                "classified_at": datetime.now().isoformat()
            }

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)

        return result

    def _classify_document(self, content: str, metadata: Dict[str, Any]) -> str:
        categories_str = "\n".join([f"{i+1}. {cat}" for i, cat in enumerate(self.categories)])

        prompt = f"""你是一个专业的技术文献分类专家。请根据文档内容，将其分类到最合适的类别中。

可用类别：
{categories_str}

文档标题：{metadata.get('title', '未知')}
文档内容预览：
{content[:3000]}

请通过长链推理分析：
1. 文档涉及的主要技术领域
2. 文档的核心主题
3. 最匹配的分类

然后返回JSON格式：
{{"category": "类别名称", "reasoning": "分类推理过程"}}
"""
        try:
            reasoning_result = llm_client.long_chain_reasoning(prompt, steps=3)

            schema = {
                "type": "object",
                "properties": {
                    "category": {"type": "string"},
                    "reasoning": {"type": "string"}
                }
            }
            result = llm_client.extract_structured_info(prompt, schema)
            category = result.get("category", "")

            if category not in self.categories:
                for cat in self.categories:
                    if cat.split("/")[0] in category or category in cat:
                        category = cat
                        break
                else:
                    category = "其他/综合"

            return category

        except Exception as e:
            print(f"分类失败: {e}")
            return "其他/综合"

    def _extract_keywords(self, content: str, metadata: Dict[str, Any]) -> List[str]:
        prompt = f"""你是一个专业的关键词提取专家。请从以下技术文献中提取{self.max_keywords}个最具代表性的关键词。

文献标题：{metadata.get('title', '未知')}
文献内容：
{content[:4000]}

关键词要求：
1. 精准反映文档核心技术内容
2. 具有检索意义
3. 包括技术术语、方法、算法等
4. 避免过于通用或宽泛的词

请返回JSON格式：
{{"keywords": ["关键词1", "关键词2", ...]}}
"""
        try:
            schema = {
                "type": "object",
                "properties": {
                    "keywords": {
                        "type": "array",
                        "items": {"type": "string"},
                        "maxItems": self.max_keywords
                    }
                }
            }
            result = llm_client.extract_structured_info(prompt, schema)
            keywords = result.get("keywords", [])

            if len(keywords) < 3:
                keywords = self._fallback_keyword_extraction(content)

            return keywords[:self.max_keywords]

        except Exception as e:
            print(f"关键词提取失败: {e}")
            return self._fallback_keyword_extraction(content)

    def _fallback_keyword_extraction(self, content: str) -> List[str]:
        important_patterns = [
            r'\b(?:机器学习|深度学习|神经网络|卷积|循环神经网络|Transformer)\b',
            r'\b(?:大数据|数据挖掘|数据分析|预测模型)\b',
            r'\b(?:云计算|容器|Docker|Kubernetes)\b',
            r'\b(?:网络安全|加密|认证|防火墙)\b',
            r'\b(?:物联网|IOT|传感器|嵌入式)\b',
            r'\b(?:区块链|分布式|共识机制)\b',
            r'\b(?:自然语言处理|NLP|文本挖掘|情感分析)\b',
            r'\b(?:计算机视觉|图像识别|目标检测|图像分割)\b',
        ]

        keywords = []
        for pattern in important_patterns:
            import re
            matches = re.findall(pattern, content)
            keywords.extend(matches)

        unique_keywords = list(set(keywords))
        return unique_keywords[:self.max_keywords]

    def _analyze_research_direction(self, content: str, category: str) -> str:
        prompt = f"""你是一个专业的技术研究分析专家。请分析以下文献的核心研究方向。

文献类别：{category}
文献内容：
{content[:3000]}

请通过长链推理：
1. 识别文献解决的核心问题
2. 采用的主要技术方案
3. 研究的创新点
4. 在技术发展脉络中的位置

返回JSON格式：
{{"research_direction": "核心研究方向描述"}}
"""
        try:
            schema = {
                "type": "object",
                "properties": {
                    "research_direction": {"type": "string"}
                }
            }
            result = llm_client.extract_structured_info(prompt, schema)
            return result.get("research_direction", "未确定研究方向")
        except Exception:
            return "未确定研究方向"

    def batch_classify(self, preprocessed_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        results = []
        for preprocessed in preprocessed_list:
            result = self.process(preprocessed)
            results.append(result)
        return results


classifier_agent = ClassifierAgent()