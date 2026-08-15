'''
Date         : 2026-08-15 18:50:22
LastEditTime : 2026-08-15 18:50:23
'''
import os
from datetime import datetime

def write_to_file(content: str, filename: str = "agent_notes.txt") -> str:
    """将内容追加写入到本地文件"""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(filename, "a", encoding="utf-8") as f:
            f.write(f"\n[{timestamp}]\n{content}\n")
            f.write("-" * 50 + "\n")
        return f"✅ 内容已保存到 {filename}"
    except Exception as e:
        return f"❌ 保存文件失败：{str(e)}"

def read_file(filename: str = "agent_notes.txt") -> str:
    """读取本地文件的内容"""
    try:
        if not os.path.exists(filename):
            return f"❌ 文件 {filename} 不存在，还没有保存过任何内容"
        
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
        
        if not content.strip():
            return f"📄 文件 {filename} 是空的"
        
        return f"📄 文件 {filename} 的内容：\n{content}"
    except Exception as e:
        return f"❌ 读取文件失败：{str(e)}"