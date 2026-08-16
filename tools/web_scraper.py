'''
Date         : 2026-08-16 13:59:38
LastEditTime : 2026-08-16 14:07:34
'''
import requests
from bs4 import BeautifulSoup

def fetch_webpage(url: str, max_length: int = 3000) -> str:
    """
    抓取指定网页的标题和正文文本内容
    """
    try:
        # 模拟浏览器请求头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        response.encoding = response.apparent_encoding or 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 移除script和style标签
        for tag in soup(['script', 'style', 'nav', 'footer']):
            tag.decompose()
        
        title = soup.find('title')
        title_text = title.get_text(strip=True) if title else "无标题"
        
        # 获取正文
        body_text = soup.get_text(separator='\n', strip=True)
        
        # 清理多余空行
        lines = [line.strip() for line in body_text.split('\n') if line.strip()]
        clean_text = '\n'.join(lines)
        
        # 截断过长的内容
        if len(clean_text) > max_length:
            clean_text = clean_text[:max_length] + "...(截断)"
        
        return f"标题：{title_text}\n\n正文内容：\n{clean_text}"
    
    except requests.exceptions.Timeout:
        return "❌ 请求超时，网站响应过慢"
    except requests.exceptions.HTTPError as e:
        return f"❌ HTTP错误：{e.response.status_code}"
    except Exception as e:
        return f"❌ 抓取失败：{str(e)}"