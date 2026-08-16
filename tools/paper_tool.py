import requests
import feedparser
import traceback

def search_papers(query: str, max_results: int = 5) -> str:
    """使用arXiv API搜索论文（不依赖arxiv库）"""
    try:
        print(f"[DEBUG] 开始搜索arXiv，关键词: {query}")
        
        url = "http://export.arxiv.org/api/query"
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": max_results,
            "sortBy": "relevance",
            "sortOrder": "descending"
        }
        
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        
        # 解析Atom XML
        feed = feedparser.parse(response.text)
        
        if not feed.entries:
            return "📚 没有找到相关论文"
        
        output = f"📚 找到 {len(feed.entries)} 篇相关论文：\n\n"
        for i, entry in enumerate(feed.entries, 1):
            title = entry.title.replace('\n', ' ').strip()
            # 获取摘要（清理HTML标签和多余空白）
            summary = entry.summary.replace('\n', ' ').strip()
            # 去掉HTML标签
            import re
            summary = re.sub(r'<[^>]+>', '', summary)
            if len(summary) > 300:
                summary = summary[:300] + "..."
            
            # 获取PDF链接
            pdf_link = entry.link.replace('/abs/', '/pdf/')
            # 获取作者
            authors = ", ".join([a.name for a in entry.authors]) if hasattr(entry, 'authors') else "未知"
            # 获取发布时间
            published = entry.published[:10] if hasattr(entry, 'published') else "未知"
            
            output += f"**{i}. {title}**\n"
            output += f"   作者：{authors}\n"
            output += f"   发布时间：{published}\n"
            output += f"   摘要：{summary}\n"
            output += f"   PDF：{pdf_link}\n\n"
        
        return output
        
    except requests.exceptions.Timeout:
        return "❌ 请求超时，arXiv API 响应过慢，请稍后再试"
    except requests.exceptions.RequestException as e:
        return f"❌ 网络请求失败：{str(e)}"
    except Exception as e:
        print(f"[ERROR] search_papers 执行失败：")
        print(traceback.format_exc())
        return f"❌ 论文搜索失败：{str(e)}"