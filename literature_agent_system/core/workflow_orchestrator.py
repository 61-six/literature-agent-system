"""
工作流编排器 - 协调多个Agent完成文献处理
"""
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

from agents.preprocessor_agent import preprocessor_agent
from agents.classifier_agent import classifier_agent
from agents.summarizer_agent import summarizer_agent
from agents.relation_analyzer_agent import relation_analyzer_agent
from core.knowledge_base import knowledge_base
from config.settings import DOCUMENTS_DIR


class WorkflowOrchestrator:
    def __init__(self):
        self.name = "WorkflowOrchestrator"
        self.agents = {
            "preprocessor": preprocessor_agent,
            "classifier": classifier_agent,
            "summarizer": summarizer_agent,
            "relation_analyzer": relation_analyzer_agent
        }

    def process_document(self, file_path: str, summary_type: str = "standard") -> Dict[str, Any]:
        workflow_id = str(uuid.uuid4())
        start_time = datetime.now()

        workflow_result = {
            "workflow_id": workflow_id,
            "status": "running",
            "file_path": file_path,
            "start_time": start_time.isoformat(),
            "steps": [],
            "final_result": None,
            "error": None
        }

        try:
            step1_result = self._run_preprocessing(workflow_id, file_path)
            workflow_result["steps"].append(step1_result)

            if step1_result.get("status") != "completed":
                workflow_result["status"] = "failed"
                workflow_result["error"] = "预处理阶段失败"
                return workflow_result

            step2_result = self._run_classification(workflow_id, step1_result)
            workflow_result["steps"].append(step2_result)

            if step2_result.get("status") != "completed":
                workflow_result["status"] = "failed"
                workflow_result["error"] = "分类标注阶段失败"
                return workflow_result

            step3_result = self._run_summarization(workflow_id, step2_result, summary_type)
            workflow_result["steps"].append(step3_result)

            if step3_result.get("status") != "completed":
                workflow_result["status"] = "failed"
                workflow_result["error"] = "摘要提取阶段失败"
                return workflow_result

            step4_result = self._run_relation_analysis(workflow_id, step3_result)
            workflow_result["steps"].append(step4_result)

            if step4_result.get("status") != "completed":
                workflow_result["status"] = "failed"
                workflow_result["error"] = "关联分析阶段失败"
                return workflow_result

            final_document = self._compile_final_document(
                workflow_id, step1_result, step2_result, step3_result, step4_result
            )

            doc_id = knowledge_base.add_document(final_document)

            final_document["doc_id"] = doc_id

            end_time = datetime.now()
            workflow_result["status"] = "completed"
            workflow_result["final_result"] = final_document
            workflow_result["end_time"] = end_time.isoformat()
            workflow_result["duration_seconds"] = (end_time - start_time).total_seconds()

        except Exception as e:
            workflow_result["status"] = "failed"
            workflow_result["error"] = str(e)

        return workflow_result

    def _run_preprocessing(self, workflow_id: str, file_path: str) -> Dict[str, Any]:
        result = preprocessor_agent.process(file_path)
        result["workflow_id"] = workflow_id
        result["step"] = 1
        result["step_name"] = "预处理"
        return result

    def _run_classification(self, workflow_id: str, preprocessed_data: Dict[str, Any]) -> Dict[str, Any]:
        result = classifier_agent.process(preprocessed_data)
        result["workflow_id"] = workflow_id
        result["step"] = 2
        result["step_name"] = "分类标注"
        return result

    def _run_summarization(
        self,
        workflow_id: str,
        classified_data: Dict[str, Any],
        summary_type: str
    ) -> Dict[str, Any]:
        result = summarizer_agent.process(classified_data, summary_type)
        result["workflow_id"] = workflow_id
        result["step"] = 3
        result["step_name"] = "摘要提取"
        return result

    def _run_relation_analysis(
        self,
        workflow_id: str,
        summarized_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        result = relation_analyzer_agent.process(summarized_data)
        result["workflow_id"] = workflow_id
        result["step"] = 4
        result["step_name"] = "关联分析"
        return result

    def _compile_final_document(
        self,
        workflow_id: str,
        preprocessed: Dict[str, Any],
        classified: Dict[str, Any],
        summarized: Dict[str, Any],
        analyzed: Dict[str, Any]
    ) -> Dict[str, Any]:
        preprocessed_output = preprocessed.get("output", {})
        classified_output = classified.get("output", {})
        summarized_output = summarized.get("output", {})
        analyzed_output = analyzed.get("output", {})

        final_document = {
            "workflow_id": workflow_id,
            "content": preprocessed_output.get("content", ""),
            "metadata": preprocessed_output.get("metadata", {}),
            "category": classified_output.get("category", ""),
            "keywords": classified_output.get("keywords", []),
            "tech_research_direction": classified_output.get("tech_research_direction", ""),
            "structured_abstract": summarized_output.get("structured_abstract", {}),
            "extracted_info": summarized_output.get("extracted_info", {}),
            "summary_type": summarized_output.get("summary_type", "standard"),
            "related_documents": analyzed_output.get("related_documents", []),
            "tech_evolution": analyzed_output.get("tech_evolution", {}),
            "recommendations": analyzed_output.get("recommendations", []),
            "tech_relations": analyzed_output.get("tech_relations", []),
            "processing_time": datetime.now().isoformat(),
            "agent_versions": {
                "preprocessor": preprocessed.get("agent", ""),
                "classifier": classified.get("agent", ""),
                "summarizer": summarized.get("agent", ""),
                "relation_analyzer": analyzed.get("agent", "")
            }
        }

        return final_document

    def batch_process(
        self,
        file_paths: List[str],
        summary_type: str = "standard"
    ) -> List[Dict[str, Any]]:
        results = []
        for file_path in file_paths:
            try:
                result = self.process_document(file_path, summary_type)
                results.append(result)
            except Exception as e:
                results.append({
                    "workflow_id": str(uuid.uuid4()),
                    "status": "failed",
                    "file_path": file_path,
                    "error": str(e)
                })
        return results

    def get_processing_status(self, doc_id: str) -> Optional[Dict[str, Any]]:
        return knowledge_base.get_document(doc_id)

    def search_documents(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        return knowledge_base.search_documents(query, limit)

    def get_all_documents(self) -> List[Dict[str, Any]]:
        return knowledge_base.get_all_documents()

    def get_statistics(self) -> Dict[str, Any]:
        return knowledge_base.get_statistics()

    def delete_document(self, doc_id: str) -> bool:
        return knowledge_base.delete_document(doc_id)


orchestrator = WorkflowOrchestrator()