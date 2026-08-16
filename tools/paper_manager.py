'''
Date         : 2026-08-16 14:39:52
LastEditTime : 2026-08-16 14:39:53
'''
import os
import json
import requests
import re
from datetime import datetime

# 知识库文件路径
KNOWLEDGE_BASE_FILE = "paper_knowledge_base.json"

def load_knowledge_base() -> dict:
    """加载知识库"""
    if os.path.exists(KNOWLEDGE_BASE_FILE):
        with open(KNOWLEDGE_BASE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"papers": []}

def save_knowledge_base(knowledge_base: dict):
    """保存知识库"""
    with open(KNOWLEDGE_BASE_FILE, "w", encoding="utf-8") as f:
        json.dump(knowledge_base, f, ensure_ascii=False, indent=2)

def download_paper(title: str = None, pdf_url: str = None, filename: str = None) -> str:
    """
    下载论文PDF到本地，并记录到知识库
    """
    try:
        if not pdf_url:
            return "❌ 请提供PDF链接"
        
        # 自动生成文件名
        if not filename:
            if title:
                # 清理标题作为文件名
                clean_title = re.sub(r'[<>:"/\\|?*]', '', title)[:50]
                filename = f"{clean_title}.pdf"
            else:
                # 从URL提取文件名
                filename = pdf_url.split('/')[-1]
                if not filename.endswith('.pdf'):
                    filename = f"paper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # 确保文件名以.pdf结尾
        if not filename.endswith('.pdf'):
            filename += '.pdf'
        
        # 下载PDF
        print(f"[DEBUG] 开始下载论文: {filename}")
        response = requests.get(pdf_url, timeout=30, stream=True)
        response.raise_for_status()
        
        # 保存到本地
        filepath = os.path.join("papers", filename)
        os.makedirs("papers", exist_ok=True)
        
        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # 记录到知识库
        kb = load_knowledge_base()
        kb["papers"].append({
            "title": title or filename.replace('.pdf', ''),
            "filename": filename,
            "path": filepath,
            "downloaded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "pdf_url": pdf_url
        })
        save_knowledge_base(kb)
        
        return f"✅ 论文下载成功！\n   文件名：{filename}\n   保存路径：{filepath}\n   已添加到知识库"
        
    except requests.exceptions.Timeout:
        return "❌ 下载超时，请检查网络连接"
    except requests.exceptions.RequestException as e:
        return f"❌ 下载失败：{str(e)}"
    except Exception as e:
        return f"❌ 下载失败：{str(e)}"

def search_local_papers(keyword: str) -> str:
    """
    在本地知识库中搜索已下载的论文
    """
    try:
        kb = load_knowledge_base()
        papers = kb.get("papers", [])
        
        if not papers:
            return "📚 本地知识库为空，还没有下载任何论文"
        
        # 关键词匹配（标题或文件名中包含关键词）
        results = []
        keyword_lower = keyword.lower()
        for p in papers:
            title = p.get("title", "").lower()
            filename = p.get("filename", "").lower()
            if keyword_lower in title or keyword_lower in filename:
                results.append(p)
        
        if not results:
            return f"📚 在本地知识库中未找到包含关键词 '{keyword}' 的论文"
        
        output = f"📚 在本地知识库中找到 {len(results)} 篇相关论文：\n\n"
        for i, p in enumerate(results, 1):
            output += f"**{i}. {p.get('title', '未知标题')}**\n"
            output += f"   文件名：{p.get('filename', '未知')}\n"
            output += f"   保存路径：{p.get('path', '未知')}\n"
            output += f"   下载时间：{p.get('downloaded_at', '未知')}\n"
            output += f"   PDF链接：{p.get('pdf_url', '无')}\n\n"
        
        return output
        
    except Exception as e:
        return f"❌ 搜索本地知识库失败：{str(e)}"

def list_all_papers() -> str:
    """
    列出本地知识库中所有论文
    """
    try:
        kb = load_knowledge_base()
        papers = kb.get("papers", [])
        
        if not papers:
            return "📚 本地知识库为空，还没有下载任何论文"
        
        output = f"📚 本地知识库共有 {len(papers)} 篇论文：\n\n"
        for i, p in enumerate(papers, 1):
            output += f"{i}. {p.get('title', '未知标题')}\n"
            output += f"   路径：{p.get('path', '未知')}\n"
            output += f"   下载时间：{p.get('downloaded_at', '未知')}\n\n"
        
        return output
        
    except Exception as e:
        return f"❌ 列出论文失败：{str(e)}"