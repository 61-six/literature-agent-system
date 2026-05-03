"""
关联分析Agent - 负责文献关联分析和参考资料推荐
"""
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from core.llm_client import llm_client
from core.knowledge_base import knowledge_base
from config.settings import RELATION_THRESHOLD


class RelationAnalyzerAgent:
    def __init__(self):
        self.name = "RelationAnalyzerAgent"
        self.description = "关联分析Agent，负责文献关联分析和参考资料推荐"
        self.threshold = RELATION_THRESHOLD

    def process(self, summarized_data: Dict[str, Any]) -> Dict[str, Any]:
        result = {
            "agent": self.name,
            "status": "pending",
            "input_doc_id": summarized_data.get("input_doc_id", ""),
            "output": {}
        }

        try:
            content = summarized_data.get("output", {}).get("content", "")
            metadata = summarized_data.get("output", {}).get("metadata", {})
            category = summarized_data.get("output", {}).get("category", "")
            keywords = summarized_data.get("output", {}).get("keywords", [])
            abstract = summarized_data.get("output", {}).get("structured_abstract", {})

            if not content:
                result["status"] = "failed"
                result["error"] = "没有内容可以关联分析"
                return result

            related_docs = self._find_related_documents(
                content, category, keywords
            )

            tech_evolution = self._analyze_tech_evolution(
                content, related_docs, category
            )

            recommendations = self._generate_recommendations(
                summarized_data, related_docs
            )

            tech_relations = self._analyze_tech_relations(
                content, related_docs, keywords
            )

            result["status"] = "completed"
            result["output"] = {
                "related_documents": related_docs,
                "tech_evolution": tech_evolution,
                "recommendations": recommendations,
                "tech_relations": tech_relations,
                "analyzed_at": datetime.now().isoformat()
            }

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)

        return result

    def _find_related_documents(
        self,
        content: str,
        category: str,
        keywords: List[str]
    ) -> List[Dict[str, Any]]:
        try:
            all_docs = knowledge_base.get_all_documents()

            if not all_docs:
                return []

            search_terms = keywords[:3] + [category.split("/")[0]]
            search_results = set()

            for term in search_terms:
                results = knowledge_base.search_documents(term, limit=10)
                for r in results:
                    search_results.add(r.get("doc_id"))

            related = []
            for doc in all_docs:
                if doc.get("doc_id") in search_results:
                    continue

                similarity_score = self._calculate_similarity(
                    content, doc.get("content", ""), keywords, doc.get("keywords", [])
                )

                if similarity_score >= self.threshold:
                    related.append({
                        "doc_id": doc.get("doc_id"),
                        "title": doc.get("metadata", {}).get("title", "未命名"),
                        "category": doc.get("category", ""),
                        "keywords": doc.get("keywords", []),
                        "similarity_score": similarity_score,
                        "abstract": doc.get("structured_abstract", {}).get("full_abstract", "")[:200]
                    })

            related.sort(key=lambda x: x["similarity_score"], reverse=True)
            return related[:10]

        except Exception as e:
            print(f"关联文档查找失败: {e}")
            return []

    def _calculate_similarity(
        self,
        content1: str,
        content2: str,
        keywords1: List[str],
        keywords2: List[str]
    ) -> float:
        keyword_overlap = len(set(keywords1) & set(keywords2))
        keyword_score = keyword_overlap / max(len(keywords1), len(keywords2), 1)

        try:
            text_similarity = llm_client.similarity_compare(content1[:2000], content2[:2000])
        except Exception:
            text_similarity = 0.5

        combined_score = (keyword_score * 0.4 + text_similarity * 0.6)

        return min(1.0, combined_score)

    def _analyze_tech_evolution(
        self,
        content: str,
        related_docs: List[Dict[str, Any]],
        category: str
    ) -> Dict[str, Any]:
        if not related_docs:
            return {
                "evolution_chain": [],
                "current_position": "这是该领域的一个新文献",
                "summary": "暂无历史文献可对比"
            }

        prompt = f"""你是一个专业的技术发展脉络分析专家。请分析以下文献在技术发展脉络中的位置。

当前文献分类：{category}
关键词：{', '.join([d.get('title', '') for d in related_docs[:5]])}

历史文献列表：
{json.dumps([{"title": d.get("title", ""), "abstract": d.get("abstract", "")[:200]} for d in related_docs[:5]], ensure_ascii=False, indent=2)}

请通过多轮推理分析：
1. 当前文献与历史文献的技术关联
2. 技术发展的演进路径
3. 当前文献在发展脉络中的位置

返回JSON格式：
{{
  "evolution_chain": ["早期技术A", "中期发展B", "当前技术C"],
  "current_position": "当前文献位置描述",
  "summary": "技术发展脉络总结"
}}
"""
        try:
            schema = {
                "type": "object",
                "properties": {
                    "evolution_chain": {"type": "array", "items": {"type": "string"}},
                    "current_position": {"type": "string"},
                    "summary": {"type": "string"}
                }
            }
            result = llm_client.extract_structured_info(prompt, schema)
            return result
        except Exception as e:
            print(f"技术脉络分析失败: {e}")
            return {
                "evolution_chain": [],
                "current_position": "分析失败",
                "summary": "技术脉络分析失败"
            }

    def _generate_recommendations(
        self,
        current_doc: Dict[str, Any],
        related_docs: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        if not related_docs:
            return []

        recommendations = []

        for doc in related_docs[:5]:
            try:
                relevance_reason = self._explain_relevance(
                    current_doc, doc
                )
                recommendations.append({
                    "doc_id": doc.get("doc_id"),
                    "title": doc.get("title", ""),
                    "relevance_reason": relevance_reason,
                    "priority": "high" if doc.get("similarity_score", 0) > 0.85 else "medium"
                })
            except Exception:
                recommendations.append({
                    "doc_id": doc.get("doc_id"),
                    "title": doc.get("title", ""),
                    "relevance_reason": "相关文献",
                    "priority": "medium"
                })

        return recommendations

    def _explain_relevance(
        self,
        current_doc: Dict[str, Any],
        related_doc: Dict[str, Any]
    ) -> str:
        prompt = f"""请解释以下两篇文献之间的技术关联。

当前文献：
标题：{current_doc.get('output', {}).get('metadata', {}).get('title', '未知')}
关键词：{', '.join(current_doc.get('output', {}).get('keywords', []))}

相关文献：
标题：{related_doc.get('title', '未知')}
关键词：{', '.join(related_doc.get('keywords', []))}

请简要说明它们之间的技术关联和参考价值（50字以内）。
"""
        try:
            messages = [
                {"role": "system", "content": "你是一个专业的技术关联分析专家。"},
                {"role": "user", "content": prompt}
            ]
            reason = llm_client.chat(messages, max_tokens=100)
            return reason.strip()
        except Exception:
            return "技术相关文献"

    def _analyze_tech_relations(
        self,
        content: str,
        related_docs: List[Dict[str, Any]],
        keywords: List[str]
    ) -> List[Dict[str, Any]]:
        if not related_docs:
            return []

        relations = []

        for doc in related_docs:
            try:
                relation_type = self._classify_relation_type(
                    content, doc, keywords
                )
                relations.append({
                    "doc_id": doc.get("doc_id"),
                    "title": doc.get("title", ""),
                    "relation_type": relation_type,
                    "similarity": doc.get("similarity_score", 0)
                })
            except Exception:
                relations.append({
                    "doc_id": doc.get("doc_id"),
                    "title": doc.get("title", ""),
                    "relation_type": "技术相关",
                    "similarity": doc.get("similarity_score", 0)
                })

        return relations

    def _classify_relation_type(
        self,
        content1: str,
        doc2: Dict[str, Any],
        keywords1: List[str]
    ) -> str:
        prompt = f"""请判断以下两篇文献的关系类型。

文献1关键词：{', '.join(keywords1)}
文献2标题：{doc2.get('title', '')}
文献2关键词：{', '.join(doc2.get('keywords', []))}

关系类型选项：
- 基础理论：文献2为文献1提供了理论基础
- 方法改进：文献2改进了文献1的方法
- 应用拓展：文献2将文献1的技术应用到新领域
- 对比研究：两篇文献采用不同方法解决相似问题
- 后续研究：文献2是文献1的延续或深入
- 技术相关：存在一般性技术关联

请返回JSON格式：
{{"relation_type": "关系类型"}}
"""
        try:
            schema = {
                "type": "object",
                "properties": {
                    "relation_type": {"type": "string"}
                }
            }
            result = llm_client.extract_structured_info(prompt, schema)
            return result.get("relation_type", "技术相关")
        except Exception:
            return "技术相关"

    def analyze_batch(
        self,
        summarized_list: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        results = []
        for summarized in summarized_list:
            result = self.process(summarized)
            results.append(result)
        return results


relation_analyzer_agent = RelationAnalyzerAgent()