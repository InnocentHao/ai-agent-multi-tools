'''
Date         : 2026-08-15 18:49:54
LastEditTime : 2026-08-15 18:49:55
'''
import serpapi
import os

serpapi_client = serpapi.Client(api_key=os.getenv("SERPAPI_API_KEY"))

def search(query: str) -> str:
    """使用SerpAPI进行真实联网搜索"""
    try:
        results = serpapi_client.search({
            "engine": "google",
            "q": query,
            "hl": "zh-cn",
            "gl": "cn",
            "num": 5
        })
        
        organic_results = results.get("organic_results", [])
        if organic_results:
            output_lines = ["📊 **以下是联网搜索到的实时信息，请优先用于回答：**\n"]
            for idx, r in enumerate(organic_results[:5], 1):
                title = r.get("title", "无标题")
                snippet = r.get("snippet", "").replace('\n', ' ').strip()
                link = r.get("link", "")
                output_lines.append(f"--- 结果 {idx} ---")
                output_lines.append(f"标题: {title}")
                output_lines.append(f"摘要: {snippet}")
                output_lines.append(f"来源: {link}")
            return "\n".join(output_lines)
        else:
            return "🔍 搜索结果为空，未找到相关信息。"
    except Exception as e:
        return f"❌ 搜索工具出现技术问题：{str(e)}"