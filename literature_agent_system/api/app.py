"""
Flask API接口 - 提供RESTful API服务
"""
import os
import json
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from pathlib import Path
import uuid
from datetime import datetime

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.workflow_orchestrator import orchestrator
from config.settings import DOCUMENTS_DIR, SUPPORTED_FORMATS

app = Flask(__name__, static_folder="../ui", static_url_path="")
CORS(app)

app.config["UPLOAD_FOLDER"] = str(DOCUMENTS_DIR)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024
app.config["ALLOWED_EXTENSIONS"] = set(SUPPORTED_FORMATS)


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "Literature Agent System",
        "timestamp": datetime.now().isoformat()
    })


@app.route("/api/documents/upload", methods=["POST"])
def upload_document():
    if "file" not in request.files:
        return jsonify({"success": False, "error": "没有文件部分"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"success": False, "error": "没有选择文件"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
        file.save(file_path)

        summary_type = request.form.get("summary_type", "standard")

        result = orchestrator.process_document(file_path, summary_type)

        if result.get("status") == "completed":
            return jsonify({
                "success": True,
                "message": "文档处理完成",
                "workflow_id": result.get("workflow_id"),
                "doc_id": result.get("final_result", {}).get("doc_id"),
                "category": result.get("final_result", {}).get("category"),
                "keywords": result.get("final_result", {}).get("keywords"),
                "duration_seconds": result.get("duration_seconds")
            })
        else:
            return jsonify({
                "success": False,
                "error": result.get("error", "处理失败")
            }), 500

    return jsonify({"success": False, "error": "不支持的文件类型"}), 400


@app.route("/api/documents", methods=["GET"])
def get_documents():
    docs = orchestrator.get_all_documents()
    return jsonify({
        "success": True,
        "documents": docs,
        "total": len(docs)
    })


@app.route("/api/documents/<doc_id>", methods=["GET"])
def get_document(doc_id):
    doc = orchestrator.get_processing_status(doc_id)
    if doc:
        return jsonify({"success": True, "document": doc})
    return jsonify({"success": False, "error": "文档不存在"}), 404


@app.route("/api/documents/<doc_id>", methods=["DELETE"])
def delete_document(doc_id):
    success = orchestrator.delete_document(doc_id)
    if success:
        return jsonify({"success": True, "message": "文档已删除"})
    return jsonify({"success": False, "error": "删除失败"}), 500


@app.route("/api/documents/search", methods=["GET"])
def search_documents():
    query = request.args.get("q", "")
    limit = int(request.args.get("limit", 10))

    if not query:
        return jsonify({"success": False, "error": "查询参数不能为空"}), 400

    results = orchestrator.search_documents(query, limit)
    return jsonify({
        "success": True,
        "query": query,
        "results": results,
        "total": len(results)
    })


@app.route("/api/statistics", methods=["GET"])
def get_statistics():
    stats = orchestrator.get_statistics()
    return jsonify({
        "success": True,
        "statistics": stats
    })


@app.route("/api/categories", methods=["GET"])
def get_categories():
    from config.settings import TECH_CATEGORIES
    return jsonify({
        "success": True,
        "categories": TECH_CATEGORIES
    })


@app.route("/api/config/summary-types", methods=["GET"])
def get_summary_types():
    from config.settings import SUMMARY_LENGTH_CONFIG
    return jsonify({
        "success": True,
        "types": [
            {"name": "brief", "description": "简短摘要", "min": SUMMARY_LENGTH_CONFIG["brief"]["min"], "max": SUMMARY_LENGTH_CONFIG["brief"]["max"]},
            {"name": "standard", "description": "标准摘要", "min": SUMMARY_LENGTH_CONFIG["standard"]["min"], "max": SUMMARY_LENGTH_CONFIG["standard"]["max"]},
            {"name": "detailed", "description": "详细摘要", "min": SUMMARY_LENGTH_CONFIG["detailed"]["min"], "max": SUMMARY_LENGTH_CONFIG["detailed"]["max"]}
        ]
    })


def create_app():
    DOCUMENTS_DIR.mkdir(exist_ok=True)
    return app


if __name__ == "__main__":
    app = create_app()
    print("=" * 60)
    print("企业文献智能整理多Agent系统 API服务")
    print("=" * 60)
    print("API地址: http://localhost:5000")
    print("访问地址: http://localhost:5000")
    print("=" * 60)
    app.run(host="0.0.0.0", port=5000, debug=True)