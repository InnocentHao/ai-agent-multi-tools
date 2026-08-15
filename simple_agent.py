'''
Date         : 2026-08-15 18:02:34
LastEditTime : 2026-08-15 18:07:08
'''
import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE")
)

from ddgs import DDGS

def search(query: str) -> str:
    """真实的联网搜索（使用ddgs）"""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            if results:
                output = "\n".join([f"- {r['title']}: {r['body'][:100]}..." for r in results])
                return f"搜索结果：\n{output}"
            else:
                return "没有找到相关结果"
    except Exception as e:
        return f"搜索出错：{str(e)}"

# 定义工具列表（OpenAI function calling格式）
tools = [{
    "type": "function",
    "function": {
        "name": "search",
        "description": "搜索互联网信息",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "搜索关键词"
                }
            },
            "required": ["query"]
        }
    }
}]

def run_agent(user_input: str):
    messages = [
        {"role": "system", "content": "你是一个智能助手，如果用户需要搜索信息，调用search工具。不需要搜索时直接回答。"},
        {"role": "user", "content": user_input}
    ]
    
    print(f"\n[用户问题] {user_input}")
    
    # 第一次调用：让模型决定是否调用工具
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    
    msg = response.choices[0].message
    print(f"[模型决策] 是否调用工具: {'是' if msg.tool_calls else '否'}")
    
    # 如果模型决定调用工具
    if msg.tool_calls:
        messages.append(msg)
        
        for tool_call in msg.tool_calls:
            # 解析参数
            args = json.loads(tool_call.function.arguments)
            # 执行工具
            result = search(args["query"])
            print(f"[工具执行] 查询: {args['query']}")
            print(f"[工具结果] {result}")
            
            # 把工具结果添加到消息
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result
            })
        
        # 第二次调用：让模型基于工具结果生成最终回答
        final_response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages
        )
        print("\n" + "="*50)
        print("🤖 最终回答：")
        print(final_response.choices[0].message.content)
    else:
        print("\n" + "="*50)
        print("🤖 直接回答：")
        print(msg.content)

if __name__ == "__main__":
    run_agent("帮我搜索一下什么是AI Agent")