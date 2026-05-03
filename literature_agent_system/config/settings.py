"""
企业文献智能整理多Agent系统配置
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
STORAGE_DIR = BASE_DIR / "storage"
DOCUMENTS_DIR = STORAGE_DIR / "documents"
KNOWLEDGE_BASE_DIR = STORAGE_DIR / "knowledge_base"

DOCUMENTS_DIR.mkdir(exist_ok=True)
KNOWLEDGE_BASE_DIR.mkdir(exist_ok=True)

LLM_CONFIG = {
    "api_type": "openai",
    "api_base": "https://api.openai.com/v1",
    "api_key": os.getenv("OPENAI_API_KEY", "your-api-key"),
    "model": "gpt-4-turbo",
    "temperature": 0.7,
    "max_tokens": 4000
}

TECH_CATEGORIES = [
    "人工智能/机器学习",
    "大数据/数据挖掘",
    "云计算/容器技术",
    "网络安全/加密算法",
    "物联网/嵌入式系统",
    "软件工程/架构设计",
    "数据库/存储技术",
    "通信网络/5G/6G",
    "区块链/分布式账本",
    "图像处理/计算机视觉",
    "自然语言处理/语音识别",
    "机器人/自动化控制",
    "材料科学/纳米技术",
    "生物医学工程",
    "新能源/储能技术",
    "量子计算/量子通信",
    "其他/综合"
]

SUMMARY_LENGTH_CONFIG = {
    "brief": {"min": 100, "max": 200},
    "standard": {"min": 300, "max": 500},
    "detailed": {"min": 800, "max": 1500}
}

RELATION_THRESHOLD = 0.75

MAX_KEYWORDS = 5
MIN_ABSTRACT_LENGTH = 100
MAX_ABSTRACT_LENGTH = 1500

SUPPORTED_FORMATS = [".pdf", ".docx", ".doc", ".txt", ".png", ".jpg", ".jpeg", ".tiff"]

VECTOR_DB_TYPE = "simple"

INDEXING_CONFIG = {
    "chunk_size": 500,
    "chunk_overlap": 50,
    "use_vector_search": True
}