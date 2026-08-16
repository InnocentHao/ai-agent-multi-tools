'''
Date         : 2026-08-16 14:44:06
LastEditTime : 2026-08-16 14:44:08
'''
import os
from pypdf import PdfReader

def read_pdf(filepath: str, max_pages: int = 5, max_chars: int = 5000) -> str:
    """
    读取PDF文件内容，返回前几页的文本（限制长度）
    """
    try:
        # 如果只传了文件名，补全路径
        if not os.path.exists(filepath):
            # 尝试在 papers 目录下找
            test_path = os.path.join("papers", filepath)
            if os.path.exists(test_path):
                filepath = test_path
            else:
                return f"❌ 文件不存在：{filepath}"
        
        reader = PdfReader(filepath)
        total_pages = len(reader.pages)
        
        # 限制读取页数
        pages_to_read = min(max_pages, total_pages)
        
        output = f"📄 文件：{os.path.basename(filepath)}\n"
        output += f"📊 总页数：{total_pages}\n"
        output += f"📖 正在读取前 {pages_to_read} 页：\n\n"
        
        full_text = ""
        for i in range(pages_to_read):
            page = reader.pages[i]
            text = page.extract_text()
            full_text += f"--- 第 {i+1} 页 ---\n{text}\n\n"
        
        # 限制总长度（避免token爆炸）
        if len(full_text) > max_chars:
            full_text = full_text[:max_chars] + "\n\n...(截断)"
        
        output += full_text
        
        return output
        
    except Exception as e:
        return f"❌ 读取PDF失败：{str(e)}"

def get_pdf_metadata(filepath: str) -> str:
    """
    获取PDF元数据（标题、作者、创建日期等）
    """
    try:
        if not os.path.exists(filepath):
            test_path = os.path.join("papers", filepath)
            if os.path.exists(test_path):
                filepath = test_path
            else:
                return f"❌ 文件不存在：{filepath}"
        
        reader = PdfReader(filepath)
        meta = reader.metadata
        
        output = f"📄 文件：{os.path.basename(filepath)}\n"
        output += f"📊 页数：{len(reader.pages)}\n"
        
        if meta:
            if meta.get('/Title'):
                output += f"📌 标题：{meta['/Title']}\n"
            if meta.get('/Author'):
                output += f"✍️ 作者：{meta['/Author']}\n"
            if meta.get('/Creator'):
                output += f"🛠️ 创建工具：{meta['/Creator']}\n"
            if meta.get('/CreationDate'):
                output += f"📅 创建日期：{meta['/CreationDate']}\n"
        else:
            output += "📋 无元数据信息"
        
        return output
        
    except Exception as e:
        return f"❌ 获取元数据失败：{str(e)}"