'''
AI Agent - 多工具智能助手
一个基于大模型和工具调用的智能代理系统
'''
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# 导入所有工具
from tools.search_tool import search
from tools.time_tool import get_current_time
from tools.calculator_tool import calculator
from tools.file_tool import write_to_file, read_file

load_dotenv()

# OpenAI客户端
openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE")
)

# ========== 工具列表 ==========
tools = [
    {
        "type": "function",
        "function": {
            "name": "search",
            "description": "搜索互联网信息，当用户需要了解最新资讯、查询资料、或任何需要联网获取信息时使用",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "搜索关键词，要具体准确"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "获取当前的日期和时间，当用户问现在几点、今天几号、星期几时使用",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "执行数学计算，支持加减乘除、幂运算和括号。当用户需要计算数值时使用",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "数学表达式，如 '2+3*4' 或 '(10+5)/3'"}
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_to_file",
            "description": "将内容保存到本地文件，当用户说'帮我记一下'、'保存这段内容'、'记录'时使用",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "要保存的内容"},
                    "filename": {"type": "string", "description": "文件名，默认 agent_notes.txt"}
                },
                "required": ["content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "读取本地文件的内容，当用户问'我之前记了什么'、'把文件内容读出来'、'查看保存的内容'时使用",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "要读取的文件名，默认 agent_notes.txt"
                    }
                },
                "required": []
            }
        }
    }
]

# 工具函数映射表
tool_functions = {
    "search": search,
    "get_current_time": get_current_time,
    "calculator": calculator,
    "write_to_file": write_to_file,
    "read_file": read_file
}

# 工具执行日志前缀
tool_emojis = {
    "search": "🔍 搜索",
    "get_current_time": "🕐 获取时间",
    "calculator": "🧮 计算",
    "write_to_file": "📝 保存文件",
    "read_file": "📖 读取文件"
}

# ========== Agent主循环 ==========

def run_agent():
    messages = [
        {"role": "system", "content": """你是一个智能助理，拥有以下能力：
1. search - 联网搜索实时信息
2. get_current_time - 获取当前时间
3. calculator - 执行数学计算
4. write_to_file - 保存内容到文件
5. read_file - 读取文件内容

请根据用户的问题，选择合适的工具来帮助回答。如果不需要工具，可以直接回答。
调用工具后，请基于工具返回的结果来回答用户。"""}
    ]
    
    print("🤖 AI Agent 已启动（支持多轮对话，输入 'exit' 退出）")
    print("📋 可用工具：搜索 🔍 | 时间 🕐 | 计算 🧮 | 保存 📝 | 读取 📖\n")
    
    while True:
        user_input = input("👤 你: ")
        if user_input.lower() in ['exit', 'quit', '退出']:
            print("👋 再见！")
            break
        
        messages.append({"role": "user", "content": user_input})
        print(f"\n[🤔 模型决策中...]")
        
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
                function_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                
                # 执行对应的工具函数
                func = tool_functions.get(function_name)
                if func:
                    if function_name == "search":
                        result = func(args["query"])
                        print(f"[🔍 搜索] 关键词: {args['query']}")
                    elif function_name == "get_current_time":
                        result = func()
                        print("[🕐 获取时间]")
                    elif function_name == "calculator":
                        result = func(args["expression"])
                        print(f"[🧮 计算] {args['expression']}")
                    elif function_name == "write_to_file":
                        result = func(args.get("content", ""), args.get("filename", "agent_notes.txt"))
                        print(f"[📝 保存文件] {args.get('filename', 'agent_notes.txt')}")
                    elif function_name == "read_file":
                        result = func(args.get("filename", "agent_notes.txt"))
                        print(f"[📖 读取文件] {args.get('filename', 'agent_notes.txt')}")
                    else:
                        result = f"未知工具: {function_name}"
                else:
                    result = f"未知工具: {function_name}"
                
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