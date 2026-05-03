"""
文档解析模块 - 支持多种格式文档的解析
"""
import os
import re
from pathlib import Path
from typing import Dict, Any, Optional
import json
from datetime import datetime

try:
    import pypdf
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

from config.settings import SUPPORTED_FORMATS


class DocumentParser:
    def __init__(self):
        self.supported_formats = SUPPORTED_FORMATS

    def parse(self, file_path: str) -> Dict[str, Any]:
        path = Path(file_path)
        suffix = path.suffix.lower()

        if not path.exists():
            return {"success": False, "error": f"文件不存在: {file_path}"}

        if suffix not in self.supported_formats:
            return {"success": False, "error": f"不支持的格式: {suffix}"}

        try:
            if suffix == ".pdf":
                return self._parse_pdf(file_path)
            elif suffix in [".docx", ".doc"]:
                return self._parse_docx(file_path)
            elif suffix == ".txt":
                return self._parse_txt(file_path)
            elif suffix in [".png", ".jpg", ".jpeg", ".tiff"]:
                return self._parse_image(file_path)
            else:
                return {"success": False, "error": f"未实现的解析器: {suffix}"}
        except Exception as e:
            return {"success": False, "error": f"解析失败: {str(e)}"}

    def _parse_pdf(self, file_path: str) -> Dict[str, Any]:
        if not PDF_AVAILABLE:
            return {"success": False, "error": "pypdf库未安装"}

        text_content = []
        metadata = {}

        try:
            with open(file_path, "rb") as f:
                reader = pypdf.PdfReader(f)
                metadata = {
                    "pages": len(reader.pages),
                    "metadata": reader.metadata if reader.metadata else {}
                }

                for page_num, page in enumerate(reader.pages):
                    text = page.extract_text()
                    if text:
                        text_content.append(f"[页{page_num + 1}]\n{text}")

            full_text = "\n\n".join(text_content)
            cleaned_text = self._clean_text(full_text)

            return {
                "success": True,
                "content": cleaned_text,
                "metadata": {
                    **metadata,
                    "file_name": os.path.basename(file_path),
                    "file_size": os.path.getsize(file_path),
                    "parse_time": datetime.now().isoformat()
                }
            }
        except Exception as e:
            return {"success": False, "error": f"PDF解析错误: {str(e)}"}

    def _parse_docx(self, file_path: str) -> Dict[str, Any]:
        if not DOCX_AVAILABLE:
            return {"success": False, "error": "python-docx库未安装"}

        try:
            doc = Document(file_path)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            full_text = "\n\n".join(paragraphs)
            cleaned_text = self._clean_text(full_text)

            metadata = {
                "paragraphs_count": len(paragraphs),
                "file_name": os.path.basename(file_path),
                "file_size": os.path.getsize(file_path),
                "parse_time": datetime.now().isoformat()
            }

            return {
                "success": True,
                "content": cleaned_text,
                "metadata": metadata
            }
        except Exception as e:
            return {"success": False, "error": f"DOCX解析错误: {str(e)}"}

    def _parse_txt(self, file_path: str) -> Dict[str, Any]:
        encodings = ["utf-8", "gbk", "gb2312", "gb18030", "latin1"]

        for encoding in encodings:
            try:
                with open(file_path, "r", encoding=encoding) as f:
                    content = f.read()

                cleaned_text = self._clean_text(content)

                return {
                    "success": True,
                    "content": cleaned_text,
                    "metadata": {
                        "encoding": encoding,
                        "file_name": os.path.basename(file_path),
                        "file_size": os.path.getsize(file_path),
                        "parse_time": datetime.now().isoformat()
                    }
                }
            except UnicodeDecodeError:
                continue

        return {"success": False, "error": "文本文件编码无法识别"}

    def _parse_image(self, file_path: str) -> Dict[str, Any]:
        if not OCR_AVAILABLE:
            return {"success": False, "error": "pytesseract或PIL库未安装，请安装: pip install pytesseract Pillow"}

        try:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image, lang="chi_sim+eng")
            cleaned_text = self._clean_text(text)

            return {
                "success": True,
                "content": cleaned_text,
                "metadata": {
                    "image_mode": image.mode,
                    "image_size": image.size,
                    "file_name": os.path.basename(file_path),
                    "file_size": os.path.getsize(file_path),
                    "parse_time": datetime.now().isoformat()
                }
            }
        except Exception as e:
            return {"success": False, "error": f"OCR识别错误: {str(e)}"}

    def _clean_text(self, text: str) -> str:
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s.,;:!?()（）【】《》""''【】、，。！？；：""''\-\+\=\*\/]', '', text)
        text = text.strip()

        return text


document_parser = DocumentParser()