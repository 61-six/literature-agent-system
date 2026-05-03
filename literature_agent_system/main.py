"""
企业文献智能整理多Agent系统 - 主程序入口
"""
import os
import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.workflow_orchestrator import orchestrator
from config.settings import DOCUMENTS_DIR, KNOWLEDGE_BASE_DIR


def print_banner():
    banner = """
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║                    企业文献智能整理多Agent系统 v1.0                           ║
║                                                                               ║
║  功能：自动化文档处理 | 智能分类标注 | 深度摘要提取 | 关联分析检索           ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_menu():
    print("\n主菜单:")
    print("  1. 上传并处理文档")
    print("  2. 批量处理文档")
    print("  3. 搜索文档")
    print("  4. 查看所有文档")
    print("  5. 查看统计信息")
    print("  6. 删除文档")
    print("  7. 启动API服务")
    print("  0. 退出系统")
    print()


def process_single_document():
    print("\n" + "=" * 60)
    print("上传并处理文档")
    print("=" * 60)

    file_path = input("请输入文档路径: ").strip()

    if not os.path.exists(file_path):
        print(f"错误: 文件不存在 - {file_path}")
        return

    print(f"\n正在处理: {file_path}")
    print("处理阶段: 预处理 -> 分类标注 -> 摘要提取 -> 关联分析")
    print("-" * 60)

    result = orchestrator.process_document(file_path, summary_type="standard")

    if result.get("status") == "completed":
        print("\n✓ 处理成功!")
        print("-" * 60)
        final = result.get("final_result", {})
        print(f"文档ID: {final.get('doc_id', 'N/A')}")
        print(f"标题: {final.get('metadata', {}).get('title', 'N/A')}")
        print(f"分类: {final.get('category', 'N/A')}")
        print(f"关键词: {', '.join(final.get('keywords', []))}")
        print(f"处理耗时: {result.get('duration_seconds', 0):.2f}秒")
        print()

        abstract = final.get("structured_abstract", {}).get("full_abstract", "")
        if abstract:
            print("摘要预览:")
            print(abstract[:500] + "..." if len(abstract) > 500 else abstract)
            print()

        related = final.get("related_documents", [])
        if related:
            print(f"关联文档 ({len(related)}篇):")
            for i, doc in enumerate(related[:3], 1):
                print(f"  {i}. {doc.get('title', 'N/A')} (相似度: {doc.get('similarity_score', 0):.2f})")
        print()
    else:
        print(f"\n✗ 处理失败: {result.get('error', '未知错误')}")


def process_batch_documents():
    print("\n" + "=" * 60)
    print("批量处理文档")
    print("=" * 60)

    folder_path = input("请输入文件夹路径: ").strip()

    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        print(f"错误: 文件夹不存在 - {folder_path}")
        return

    supported_extensions = ['.pdf', '.docx', '.doc', '.txt', '.png', '.jpg', '.jpeg', '.tiff']
    files = []
    for ext in supported_extensions:
        files.extend(Path(folder_path).glob(f"*{ext}"))
        files.extend(Path(folder_path).glob(f"*{ext.upper()}"))

    if not files:
        print(f"在 {folder_path} 中未找到支持的文档")
        return

    print(f"\n找到 {len(files)} 个文档:")
    for i, f in enumerate(files, 1):
        print(f"  {i}. {f.name}")
    print()

    confirm = input("是否开始处理? (y/n): ").strip().lower()
    if confirm != 'y':
        return

    print(f"\n开始批量处理...")
    print("-" * 60)

    file_paths = [str(f) for f in files]
    results = orchestrator.batch_process(file_paths, summary_type="standard")

    success_count = sum(1 for r in results if r.get("status") == "completed")
    fail_count = len(results) - success_count

    print("\n" + "=" * 60)
    print("批量处理完成")
    print("=" * 60)
    print(f"总计: {len(results)} | 成功: {success_count} | 失败: {fail_count}")
    print()


def search_documents():
    print("\n" + "=" * 60)
    print("搜索文档")
    print("=" * 60)

    query = input("请输入搜索关键词: ").strip()

    if not query:
        print("搜索关键词不能为空")
        return

    results = orchestrator.search_documents(query, limit=20)

    if not results:
        print("未找到匹配的文档")
        return

    print(f"\n找到 {len(results)} 篇相关文档:")
    print("-" * 60)

    for i, doc in enumerate(results, 1):
        print(f"{i}. {doc.get('metadata', {}).get('title', 'N/A')}")
        print(f"   分类: {doc.get('category', 'N/A')} | 关键词: {', '.join(doc.get('keywords', [])[:5])}")
        abstract = doc.get('structured_abstract', {}).get('full_abstract', '')
        if abstract:
            print(f"   摘要: {abstract[:200]}...")
        print()


def list_all_documents():
    print("\n" + "=" * 60)
    print("所有文档列表")
    print("=" * 60)

    docs = orchestrator.get_all_documents()

    if not docs:
        print("知识库中暂无文档")
        return

    print(f"\n共 {len(docs)} 篇文档:")
    print("-" * 60)

    for i, doc in enumerate(docs, 1):
        print(f"{i}. {doc.get('metadata', {}).get('title', 'N/A')}")
        print(f"   ID: {doc.get('doc_id', 'N/A')}")
        print(f"   分类: {doc.get('category', 'N/A')}")
        print(f"   关键词: {', '.join(doc.get('keywords', [])[:5])}")
        print(f"   添加时间: {doc.get('added_time', 'N/A')}")
        print()


def show_statistics():
    print("\n" + "=" * 60)
    print("统计信息")
    print("=" * 60)

    stats = orchestrator.get_statistics()

    print(f"\n总文档数: {stats.get('total_documents', 0)}")
    print(f"总关键词数: {stats.get('total_keywords', 0)}")
    print(f"平均每文档关键词数: {stats.get('avg_keywords_per_doc', 0):.1f}")
    print()

    categories = stats.get('categories', {})
    if categories:
        print("分类分布:")
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            bar = "█" * count
            print(f"  {cat}: {count} {bar}")
    print()


def delete_document():
    print("\n" + "=" * 60)
    print("删除文档")
    print("=" * 60)

    doc_id = input("请输入要删除的文档ID: ").strip()

    if not doc_id:
        print("文档ID不能为空")
        return

    confirm = input(f"确定要删除文档 {doc_id} 吗? (y/n): ").strip().lower()
    if confirm != 'y':
        return

    success = orchestrator.delete_document(doc_id)

    if success:
        print("✓ 文档已删除")
    else:
        print("✗ 删除失败，文档可能不存在")


def start_api_server():
    print("\n" + "=" * 60)
    print("启动API服务")
    print("=" * 60)
    print("\n正在启动Flask API服务...")
    print("API地址: http://localhost:5000")
    print("访问地址: http://localhost:5000")
    print("\n按 Ctrl+C 停止服务")
    print("-" * 60)

    from api.app import app
    app.run(host="0.0.0.0", port=5000, debug=False)


def main():
    print_banner()

    while True:
        print_menu()
        choice = input("请选择操作 [0-7]: ").strip()

        if choice == "1":
            process_single_document()
        elif choice == "2":
            process_batch_documents()
        elif choice == "3":
            search_documents()
        elif choice == "4":
            list_all_documents()
        elif choice == "5":
            show_statistics()
        elif choice == "6":
            delete_document()
        elif choice == "7":
            start_api_server()
        elif choice == "0":
            print("\n感谢使用企业文献智能整理多Agent系统!")
            print("再见!")
            break
        else:
            print("\n无效选择，请重新输入")

        input("\n按回车键继续...")


if __name__ == "__main__":
    main()