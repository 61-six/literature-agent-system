"""
企业文献智能整理多Agent系统
"""

__version__ = "1.0.0"
__author__ = "Enterprise R&D Team"

from core.workflow_orchestrator import orchestrator
from agents import (
    preprocessor_agent,
    classifier_agent,
    summarizer_agent,
    relation_analyzer_agent
)

__all__ = [
    "orchestrator",
    "preprocessor_agent",
    "classifier_agent",
    "summarizer_agent",
    "relation_analyzer_agent"
]