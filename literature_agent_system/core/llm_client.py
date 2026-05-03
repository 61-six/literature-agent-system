"""
大语言模型接口封装
"""
import json
from typing import List, Dict, Any, Optional
from openai import OpenAI
from config.settings import LLM_CONFIG


class LLMClient:
    def __init__(self):
        self.client = OpenAI(
            api_key=LLM_CONFIG["api_key"],
            base_url=LLM_CONFIG["api_base"]
        )
        self.model = LLM_CONFIG["model"]
        self.temperature = LLM_CONFIG["temperature"]
        self.max_tokens = LLM_CONFIG["max_tokens"]

    def chat(self, messages: List[Dict[str, str]], temperature: Optional[float] = None,
             max_tokens: Optional[int] = None) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature or self.temperature,
            max_tokens=max_tokens or self.max_tokens
        )
        return response.choices[0].message.content

    def long_chain_reasoning(self, prompt: str, steps: int = 3) -> str:
        messages = [
            {"role": "system", "content": f"你是一个专业的技术文献分析专家。请通过{steps}步逻辑推理来分析和回答问题。"},
            {"role": "user", "content": prompt}
        ]
        reasoning_prompt = f"""
请逐步推理分析以下问题：

{prompt}

推理步骤：
"""
        messages[1]["content"] = reasoning_prompt
        return self.chat(messages, temperature=0.3)

    def extract_structured_info(self, prompt: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        messages = [
            {"role": "system", "content": f"你是一个专业的信息提取专家。请根据以下JSON schema提取信息：{json.dumps(schema, ensure_ascii=False)}"},
            {"role": "user", "content": prompt}
        ]
        response = self.chat(messages, temperature=0.3)
        try:
            return json.loads(response)
        except:
            return {"error": "解析失败", "raw_response": response}

    def similarity_compare(self, text1: str, text2: str) -> float:
        messages = [
            {"role": "system", "content": "你是一个专业的语义相似度分析专家。请分析两段文本的语义相似度，返回0-1之间的数值，1表示完全相似。"},
            {"role": "user", "content": f"文本1：{text1}\n\n文本2：{text2}\n\n请返回相似度分数："}
        ]
        response = self.chat(messages, temperature=0.1)
        try:
            score = float(response.strip())
            return max(0.0, min(1.0, score))
        except:
            return 0.0


llm_client = LLMClient()