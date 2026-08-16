import os
from pypdf import PdfReader

def read_paper_content(filepath: str, max_pages: int = 10) -> str:
    """
    读取论文PDF内容，返回文本（最多max_pages页）
    """
    try:
        if not os.path.exists(filepath):
            test_path = os.path.join("papers", filepath)
            if os.path.exists(test_path):
                filepath = test_path
            else:
                return f"❌ 文件不存在：{filepath}"
        
        reader = PdfReader(filepath)
        total_pages = len(reader.pages)
        pages_to_read = min(total_pages, max_pages)
        
        full_text = ""
        for i in range(pages_to_read):
            page = reader.pages[i]
            text = page.extract_text()
            full_text += text + "\n\n"
        
        # 截断过长内容
        if len(full_text) > 8000:
            full_text = full_text[:8000] + "\n\n...(截断)"
        
        return full_text
        
    except Exception as e:
        return f"❌ 读取论文失败：{str(e)}"


def summarize_paper(filepath: str, openai_client, model: str = "deepseek-chat") -> str:
    """
    读取论文并调用大模型生成结构化总结
    """
    try:
        # 1. 读取论文内容
        content = read_paper_content(filepath, max_pages=10)
        if content.startswith("❌"):
            return content
        
        # 2. 构建总结提示词
        prompt = f"""
请对以下论文内容生成结构化中文总结，格式如下：

## 📌 论文标题
（从内容中提取）

## 👨‍💻 作者
（从内容中提取）

## 🎯 研究背景与动机
（1-2句话说明为什么做这个研究）

## ❓ 核心问题
（1句话概括论文要解决什么问题）

## 🏗️ 方法 / 架构
（3-5个要点，描述提出的方法或系统架构）

## 🔬 实验与结果
（2-3个要点，说明实验设置和主要结果）

## 💡 主要贡献
（2-3个要点，总结论文的贡献）

## ⚠️ 局限性（如有）
（可选，1-2个要点）

---
论文内容：
{content}
---
请严格按照上述格式输出总结，如果某些信息在内容中未提及，请标注"未提及"。
"""
        
        # 3. 调用大模型
        response = openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "你是一个专业的学术论文总结助手，擅长提取论文的核心信息并结构化呈现。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        
        summary = response.choices[0].message.content
        
        # 4. 返回结果
        return f"📄 **论文总结**\n\n{summary}"
        
    except Exception as e:
        return f"❌ 生成总结失败：{str(e)}"