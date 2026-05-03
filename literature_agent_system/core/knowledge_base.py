"""
知识库管理模块 - 存储和管理处理后的文献
"""
import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from config.settings import KNOWLEDGE_BASE_DIR, VECTOR_DB_TYPE


class KnowledgeBase:
    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or KNOWLEDGE_BASE_DIR
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.documents_file = self.base_dir / "documents.json"
        self.vectors_file = self.base_dir / "vectors.json"
        self._init_storage()

    def _init_storage(self):
        if not self.documents_file.exists():
            self._save_json(self.documents_file, {"documents": []})
        if not self.vectors_file.exists():
            self._save_json(self.vectors_file, {"vectors": []})

    def _load_json(self, file_path: Path) -> Dict[str, Any]:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_json(self, file_path: Path, data: Dict[str, Any]):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add_document(self, doc_data: Dict[str, Any]) -> str:
        doc_id = doc_data.get("doc_id") or self._generate_doc_id()
        doc_data["doc_id"] = doc_id
        doc_data["added_time"] = datetime.now().isoformat()

        storage = self._load_json(self.documents_file)
        documents = storage.get("documents", [])

        existing_idx = None
        for i, d in enumerate(documents):
            if d.get("doc_id") == doc_id:
                existing_idx = i
                break

        if existing_idx is not None:
            documents[existing_idx] = doc_data
        else:
            documents.append(doc_data)

        storage["documents"] = documents
        self._save_json(self.documents_file, storage)

        return doc_id

    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        storage = self._load_json(self.documents_file)
        documents = storage.get("documents", [])

        for doc in documents:
            if doc.get("doc_id") == doc_id:
                return doc
        return None

    def get_all_documents(self) -> List[Dict[str, Any]]:
        storage = self._load_json(self.documents_file)
        return storage.get("documents", [])

    def search_documents(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        storage = self._load_json(self.documents_file)
        documents = storage.get("documents", [])

        query_lower = query.lower()
        results = []

        for doc in documents:
            score = 0
            text_content = (
                doc.get("content", "") + " " +
                doc.get("title", "") + " " +
                " ".join(doc.get("keywords", [])) + " " +
                doc.get("category", "")
            ).lower()

            if query_lower in text_content:
                score = text_content.count(query_lower)

            if score > 0:
                results.append((score, doc))

        results.sort(key=lambda x: x[0], reverse=True)
        return [doc for _, doc in results[:limit]]

    def delete_document(self, doc_id: str) -> bool:
        storage = self._load_json(self.documents_file)
        documents = storage.get("documents", [])

        original_len = len(documents)
        documents = [d for d in documents if d.get("doc_id") != doc_id]

        if len(documents) < original_len:
            storage["documents"] = documents
            self._save_json(self.documents_file, storage)
            return True
        return False

    def update_document(self, doc_id: str, updates: Dict[str, Any]) -> bool:
        storage = self._load_json(self.documents_file)
        documents = storage.get("documents", [])

        for i, doc in enumerate(documents):
            if doc.get("doc_id") == doc_id:
                documents[i].update(updates)
                documents[i]["updated_time"] = datetime.now().isoformat()
                storage["documents"] = documents
                self._save_json(self.documents_file, storage)
                return True
        return False

    def add_vector(self, doc_id: str, vector: List[float], chunk_id: str = ""):
        storage = self._load_json(self.vectors_file)
        vectors = storage.get("vectors", [])

        vectors = [v for v in vectors if not (v.get("doc_id") == doc_id and v.get("chunk_id") == chunk_id)]

        vectors.append({
            "doc_id": doc_id,
            "chunk_id": chunk_id,
            "vector": vector,
            "created_time": datetime.now().isoformat()
        })

        storage["vectors"] = vectors
        self._save_json(self.vectors_file, storage)

    def find_similar(self, query_vector: List[float], limit: int = 5, threshold: float = 0.75) -> List[Dict[str, Any]]:
        storage = self._load_json(self.vectors_file)
        vectors = storage.get("vectors", [])
        docs_storage = self._load_json(self.documents_file)
        documents = {d.get("doc_id"): d for d in docs_storage.get("documents", [])}

        results = []
        for v in vectors:
            similarity = self._cosine_similarity(query_vector, v.get("vector", []))
            if similarity >= threshold:
                doc = documents.get(v.get("doc_id"))
                if doc:
                    results.append({
                        "doc_id": v.get("doc_id"),
                        "chunk_id": v.get("chunk_id"),
                        "similarity": similarity,
                        "document": doc
                    })

        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:limit]

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def _generate_doc_id(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        return f"doc_{timestamp}"

    def get_statistics(self) -> Dict[str, Any]:
        storage = self._load_json(self.documents_file)
        documents = storage.get("documents", [])

        categories = {}
        total_keywords = 0

        for doc in documents:
            cat = doc.get("category", "未分类")
            categories[cat] = categories.get(cat, 0) + 1
            total_keywords += len(doc.get("keywords", []))

        return {
            "total_documents": len(documents),
            "categories": categories,
            "total_keywords": total_keywords,
            "avg_keywords_per_doc": total_keywords / len(documents) if documents else 0
        }


knowledge_base = KnowledgeBase()