'''
Date         : 2026-08-15 18:08:29
LastEditTime : 2026-08-15 18:34:59
'''
import os
import json
import serpapi
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# 1. OpenAI客户端（用于大模型对话）
openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE")
)

# 2. SerpAPI客户端（用于搜索引擎）
serpapi_client = serpapi.Client(api_key=os.getenv("SERPAPI_API_KEY"))

def search(query: str) -> str:
    """使用SerpAPI进行真实联网搜索，并返回结构化结果"""
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
            # 精简并结构化输出
            output_lines = ["📊 **以下是联网搜索到的实时信息，请优先用于回答：**\n"]
            for idx, r in enumerate(organic_results[:5], 1):
                title = r.get("title", "无标题")
                snippet = r.get("snippet", "")
                link = r.get("link", "")
                
                # 清理snippet中可能存在的换行符和多余空格
                snippet = snippet.replace('\n', ' ').strip()
                
                output_lines.append(f"--- 结果 {idx} ---")
                output_lines.append(f"标题: {title}")
                output_lines.append(f"摘要: {snippet}")
                output_lines.append(f"来源: {link}")
            
            return "\n".join(output_lines)
        else:
            return "🔍 搜索结果为空，未找到相关信息。"
            
    except Exception as e:
        return f"❌ 搜索工具出现技术问题：{str(e)}"

# ✅ 加在这里：定义工具列表
tools = [{
    "type": "function",
    "function": {
        "name": "search",
        "description": "搜索互联网信息，当用户需要了解最新资讯、查询资料、或任何需要联网获取信息时使用",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "搜索关键词，要具体准确"
                }
            },
            "required": ["query"]
        }
    }
}]

def run_agent():
    messages = [
    {"role": "system", "content": """你是一个严谨的智能助手。当用户提问时，请遵循以下规则：
1.  **优先使用工具**：如果问题涉及实时信息、最新数据或具体事实，请优先调用 `search` 工具。
2.  **严格依据搜索结果**：在获得搜索结果后，你的回答**必须**基于搜索到的信息。如果搜索结果与你的内部知识有冲突，以**搜索结果为准**。
3.  **引用来源**：在回答中，要尽量引用搜索结果的标题或摘要，增加可信度。
4.  **无法获取信息时**：如果搜索无结果，再基于你的内部知识进行回答，但要明确告知用户“搜索结果未找到相关信息，以下是基于知识库的回答”。"""}
]
    
    print("🤖 AI Agent 已启动（支持多轮对话，输入 'exit' 退出）\n")
    
    while True:
        user_input = input("👤 你: ")
        if user_input.lower() in ['exit', 'quit', '退出']:
            print("👋 再见！")
            break
        
        messages.append({"role": "user", "content": user_input})
        print(f"\n[模型决策中...]")
        
        response = openai_client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        
        msg = response.choices[0].message
        
        if msg.tool_calls:
            messages.append(msg)
            for tool_call in msg.tool_calls:
                args = json.loads(tool_call.function.arguments)
                result = search(args["query"])
                print(f"[工具调用] 搜索: {args['query']}")
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })
            
            final_response = openai_client.chat.completions.create(
                model="deepseek-chat",
                messages=messages
            )
            final_msg = final_response.choices[0].message
            messages.append(final_msg)
            print(f"\n🤖 助手: {final_msg.content}\n")
        else:
            messages.append(msg)
            print(f"\n🤖 助手: {msg.content}\n")

if __name__ == "__main__":
    run_agent()