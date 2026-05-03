"""
摘要提取Agent - 负责深度信息抽取和结构化摘要生成
"""
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from core.llm_client import llm_client
from config.settings import SUMMARY_LENGTH_CONFIG, MIN_ABSTRACT_LENGTH, MAX_ABSTRACT_LENGTH


class SummarizerAgent:
    def __init__(self):
        self.name = "SummarizerAgent"
        self.description = "摘要提取Agent，负责深度信息抽取和结构化摘要生成"
        self.length_config = SUMMARY_LENGTH_CONFIG

    def process(self, classified_data: Dict[str, Any], summary_type: str = "standard") -> Dict[str, Any]:
        result = {
            "agent": self.name,
            "status": "pending",
            "input_doc_id": classified_data.get("input_doc_id", ""),
            "output": {}
        }

        try:
            content = classified_data.get("output", {}).get("content", "")
            metadata = classified_data.get("output", {}).get("metadata", {})
            category = classified_data.get("output", {}).get("category", "")
            keywords = classified_data.get("output", {}).get("keywords", [])
            research_direction = classified_data.get("output", {}).get("tech_research_direction", "")

            if not content:
                result["status"] = "failed"
                result["error"] = "没有内容可以摘要"
                return result

            length_cfg = self.length_config.get(summary_type, self.length_config["standard"])
            min_len = length_cfg["min"]
            max_len = length_cfg["max"]

            extracted_info = self._extract_structured_info(content, min_len, max_len)

            structured_abstract = self._generate_structured_abstract(
                content, metadata, category, keywords, research_direction, extracted_info, summary_type
            )

            result["status"] = "completed"
            result["output"] = {
                "summary_type": summary_type,
                "structured_abstract": structured_abstract,
                "extracted_info": extracted_info,
                "summarized_at": datetime.now().isoformat()
            }

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)

        return result

    def _extract_structured_info(self, content: str, min_len: int, max_len: int) -> Dict[str, Any]:
        prompt = f"""你是一个专业的技术文献信息提取专家。请从以下文献中提取结构化信息。

文献内容：
{content[:6000]}

请提取以下四个模块的信息：

1. 技术结论（Technical Conclusions）：
   - 文档的核心技术结论是什么？
   - 主要的技术发现或成果？

2. 实验数据（Experimental Data）：
   - 有哪些重要实验数据或性能指标？
   - 实验方法是什么？

3. 创新点（Innovations）：
   - 文档的主要创新点是什么？
   - 相较于现有方法有什么改进？

4. 待解决问题（Open Problems）：
   - 文档提出了哪些待解决的问题？
   - 未来研究方向是什么？

请返回JSON格式：
{{
  "technical_conclusions": "技术结论内容...",
  "experimental_data": "实验数据内容...",
  "innovations": "创新点内容...",
  "open_problems": "待解决问题内容..."
}}
"""
        try:
            schema = {
                "type": "object",
                "properties": {
                    "technical_conclusions": {"type": "string"},
                    "experimental_data": {"type": "string"},
                    "innovations": {"type": "string"},
                    "open_problems": {"type": "string"}
                }
            }
            result = llm_client.extract_structured_info(prompt, schema)
            return result
        except Exception as e:
            print(f"信息提取失败: {e}")
            return {
                "technical_conclusions": "提取失败",
                "experimental_data": "提取失败",
                "innovations": "提取失败",
                "open_problems": "提取失败"
            }

    def _generate_structured_abstract(
        self,
        content: str,
        metadata: Dict[str, Any],
        category: str,
        keywords: List[str],
        research_direction: str,
        extracted_info: Dict[str, Any],
        summary_type: str
    ) -> Dict[str, Any]:
        length_cfg = self.length_config.get(summary_type, self.length_config["standard"])
        target_length = f"{length_cfg['min']}-{length_cfg['max']}字"

        prompt = f"""你是一个专业的学术摘要生成专家。请根据以下信息生成高质量的结构化摘要。

文献基本信息：
- 标题：{metadata.get('title', '未知')}
- 作者：{', '.join(metadata.get('authors', [])) or '未知'}
- 发表时间：{metadata.get('publication_date', '未知')}
- 技术分类：{category}
- 关键词：{', '.join(keywords)}
- 研究方向：{research_direction}

文献详细分析：
{json.dumps(extracted_info, ensure_ascii=False, indent=2)}

文献完整内容预览：
{content[:3000]}

请生成{summary_type}级别的摘要（目标长度：{target_length}），包含：
1. 背景与目的
2. 方法与技术
3. 主要成果
4. 结论与意义

使用长链推理确保摘要逻辑连贯、语义完整。

请返回JSON格式：
{{
  "background": "背景与目的...",
  "methods": "方法与技术...",
  "results": "主要成果...",
  "conclusion": "结论与意义...",
  "full_abstract": "完整摘要文本..."
}}
"""
        try:
            reasoning_prompt = f"""
请通过三步长链推理分析并生成摘要：

第一步：理解文献背景
{prompt}

第二步：分析技术方案
根据文献内容和提取的信息，分析所采用的技术方案。

第三步：总结核心贡献
综合以上分析，给出文献的核心贡献和价值。

最终摘要输出（{target_length}）：
"""
            llm_client.long_chain_reasoning(reasoning_prompt, steps=3)

            schema = {
                "type": "object",
                "properties": {
                    "background": {"type": "string"},
                    "methods": {"type": "string"},
                    "results": {"type": "string"},
                    "conclusion": {"type": "string"},
                    "full_abstract": {"type": "string"}
                }
            }
            result = llm_client.extract_structured_info(prompt, schema)

            full_abstract = result.get("full_abstract", "")
            if len(full_abstract) < MIN_ABSTRACT_LENGTH:
                full_abstract = self._expand_abstract(full_abstract, content, target_length)

            result["full_abstract"] = self._truncate_abstract(full_abstract, MAX_ABSTRACT_LENGTH)

            return result

        except Exception as e:
            print(f"摘要生成失败: {e}")
            return {
                "background": "生成失败",
                "methods": "生成失败",
                "results": "生成失败",
                "conclusion": "生成失败",
                "full_abstract": "摘要生成失败，请手动处理。"
            }

    def _expand_abstract(self, abstract: str, content: str, target_length: str) -> str:
        prompt = f"""请扩展以下摘要至{target_length}，保持内容连贯性和信息完整性。

当前摘要：
{abstract}

文献内容补充：
{content[:2000]}
"""
        try:
            messages = [
                {"role": "system", "content": "你是一个专业的摘要扩展专家。"},
                {"role": "user", "content": prompt}
            ]
            expanded = llm_client.chat(messages)
            return expanded
        except Exception:
            return abstract

    def _truncate_abstract(self, abstract: str, max_length: int) -> str:
        if len(abstract) <= max_length:
            return abstract

        truncate_at = abstract.rfind('。', 0, max_length)
        if truncate_at > max_length * 0.7:
            return abstract[:truncate_at + 1]
        return abstract[:max_length] + "..."

    def batch_summarize(
        self,
        classified_list: List[Dict[str, Any]],
        summary_type: str = "standard"
    ) -> List[Dict[str, Any]]:
        results = []
        for classified in classified_list:
            result = self.process(classified, summary_type)
            results.append(result)
        return results


summarizer_agent = SummarizerAgent()