"""
预处理Agent - 负责文档格式转换、OCR识别和元信息提取
"""
import re
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
import uuid

from core.document_parser import document_parser
from core.llm_client import llm_client


class PreprocessorAgent:
    def __init__(self):
        self.name = "PreprocessorAgent"
        self.description = "文档预处理Agent，负责格式转换、OCR识别和元信息提取"

    def process(self, file_path: str) -> Dict[str, Any]:
        result = {
            "agent": self.name,
            "status": "pending",
            "input_file": file_path,
            "output": {}
        }

        try:
            parse_result = document_parser.parse(file_path)

            if not parse_result.get("success"):
                result["status"] = "failed"
                result["error"] = parse_result.get("error", "未知解析错误")
                return result

            content = parse_result.get("content", "")
            metadata = parse_result.get("metadata", {})

            extracted_metadata = self._extract_metadata(content, metadata)

            cleaned_content = self._clean_content(content)

            result["status"] = "completed"
            result["output"] = {
                "content": cleaned_content,
                "metadata": extracted_metadata,
                "original_metadata": metadata,
                "word_count": len(cleaned_content),
                "char_count": len(cleaned_content),
                "preprocessed_at": datetime.now().isoformat()
            }

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)

        return result

    def _extract_metadata(self, content: str, original_metadata: Dict[str, Any]) -> Dict[str, Any]:
        metadata = {
            "title": "",
            "authors": [],
            "publication_date": "",
            "project_direction": "",
            "source": original_metadata.get("file_name", ""),
            "file_size": original_metadata.get("file_size", 0),
            "pages": original_metadata.get("pages", 1)
        }

        title_patterns = [
            r"^#\s+(.+)$",
            r"^(.{5,50})\n[=\-]+",
            r"标题[：:]\s*(.+)",
            r"^(.{10,100})$"
        ]

        first_lines = content.split("\n")[:20]
        for line in first_lines:
            line = line.strip()
            if len(line) > 10 and len(line) < 200:
                for pattern in title_patterns:
                    match = re.match(pattern, line, re.MULTILINE)
                    if match:
                        potential_title = match.group(1).strip()
                        if len(potential_title) > 5 and not any(c in potential_title for c in ["图表", "目录", "摘要", "Abstract"]):
                            metadata["title"] = potential_title
                            break
                if metadata["title"]:
                    break

        if not metadata["title"]:
            metadata["title"] = original_metadata.get("file_name", "未命名文档")

        author_patterns = [
            r"作者[：:]\s*(.+)",
            r"Author[s]?[：:]\s*(.+)",
            r"(.+?)等?[研研完完]究员",
            r"(.+?)工程师"
        ]

        for line in first_lines[:30]:
            for pattern in author_patterns:
                match = re.search(pattern, line)
                if match:
                    potential_author = match.group(1).strip()
                    if len(potential_author) > 1 and len(potential_author) < 50:
                        metadata["authors"] = [a.strip() for a in potential_author.split(",")]
                        break
            if metadata["authors"]:
                break

        date_patterns = [
            r"(\d{4})年(\d{1,2})月(\d{1,2})日",
            r"(\d{4})-(\d{2})-(\d{2})",
            r"(\d{4})/(\d{2})/(\d{2})",
            r"(\d{4})年(\d{1,2})月",
            r"(\d{4})年"
        ]

        content_sample = content[:2000]
        for pattern in date_patterns:
            match = re.search(pattern, content_sample)
            if match:
                if len(match.groups()) >= 1:
                    metadata["publication_date"] = match.group(0)
                    break

        if not metadata["publication_date"]:
            metadata["publication_date"] = datetime.now().strftime("%Y-%m-%d")

        try:
            kb_prompt = f"""从以下文档内容中提取技术领域和项目方向信息。

文档内容预览：
{content[:3000]}

请提取：
1. 技术领域/研究方向
2. 可能所属的项目方向

用JSON格式返回：
{{"tech_domain": "领域", "project_direction": "项目方向"}}
"""
            schema = {
                "type": "object",
                "properties": {
                    "tech_domain": {"type": "string"},
                    "project_direction": {"type": "string"}
                }
            }
            extracted = llm_client.extract_structured_info(kb_prompt, schema)
            metadata["tech_domain"] = extracted.get("tech_domain", "")
            metadata["project_direction"] = extracted.get("project_direction", "")
        except Exception:
            metadata["tech_domain"] = ""
            metadata["project_direction"] = ""

        return metadata

    def _clean_content(self, content: str) -> str:
        content = re.sub(r'\n{3,}', '\n\n', content)
        content = re.sub(r'[ \t]+', ' ', content)
        content = re.sub(r'\[\d+\]', '', content)
        content = re.sub(r'\(cid:\d+\)', '', content)

        lines = content.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if len(line) > 0:
                cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    def batch_process(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        results = []
        for file_path in file_paths:
            result = self.process(file_path)
            results.append(result)
        return results


preprocessor_agent = PreprocessorAgent()