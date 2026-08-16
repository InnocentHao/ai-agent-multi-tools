'''
Date         : 2026-08-15 17:29:17
LastEditTime : 2026-08-16 14:22:25
'''
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
from tools.web_scraper import fetch_webpage      
from tools.execute_python import execute_python
from tools.paper_tool import search_papers

load_dotenv()

# OpenAI客户端
openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE")
)

def compress_conversation(messages: list) -> list:
    """
    压缩对话历史：保留最近15轮，把更早的对话压缩成摘要
    """
    RECENT_TURNS = 15
    RECENT_MESSAGES = RECENT_TURNS * 2  # 用户+助手交替
    
    if len(messages) <= RECENT_MESSAGES + 2:
        return messages
    
    # ====== 工具函数：安全获取消息内容 ======
    def get_role(msg):
        if hasattr(msg, 'role'):
            return msg.role
        return msg.get('role', '')
    
    def get_content(msg):
        if hasattr(msg, 'content'):
            return msg.content
        return msg.get('content', '')
    
    # ====== 分离系统消息 ======
    system_messages = [m for m in messages if get_role(m) == 'system']
    non_system = [m for m in messages if get_role(m) != 'system']
    
    # 最近的对话
    recent_messages = non_system[-RECENT_MESSAGES:]
    old_messages = non_system[:-RECENT_MESSAGES]
    
    # ====== 压缩旧对话 ======
    if old_messages:
        history_text = []
        for m in old_messages:
            role = get_role(m)
            content = get_content(m)
            if role == 'user':
                history_text.append(f"用户：{content}")
            elif role == 'assistant':
                history_text.append(f"助手：{content[:200]}")  # 截断过长内容
        
        summary_prompt = [
            {"role": "system", "content": "请将下面的对话历史压缩成一段简洁的摘要（不超过200字），只保留关键信息、重要结论和事实。"},
            {"role": "user", "content": "对话历史：\n" + "\n".join(history_text)}
        ]
        
        try:
            summary_response = openai_client.chat.completions.create(
                model="deepseek-chat",
                messages=summary_prompt,
                temperature=0.3
            )
            summary = summary_response.choices[0].message.content
        except Exception as e:
            summary = f"[对话摘要生成失败：{str(e)}]"
        
        # 构建新的消息列表
        compressed_messages = system_messages + [
            {"role": "system", "content": f"【历史对话摘要】\n{summary}"}
        ] + recent_messages
        
        print(f"[🧠 记忆压缩] 已压缩 {len(old_messages)} 条旧消息，保留最近 {len(recent_messages)} 条")
        return compressed_messages
    
    return messages

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
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_webpage",
            "description": "抓取指定网页的标题和正文内容，当用户需要查看某个网页的具体内容时使用",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "要抓取的网页完整URL地址，如 https://www.python.org/"
                    }
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "execute_python",
            "description": "执行Python代码并返回运行结果，当用户需要测试代码片段、计算复杂逻辑时使用",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "要执行的Python代码"
                    },
                    "timeout_seconds": {
                        "type": "integer",
                        "description": "超时时间（秒），默认10秒"
                    }
                },
                "required": ["code"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_papers",
            "description": "在arXiv上搜索学术论文，当用户需要查找论文、文献、研究资料时使用",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词，如 'multi-agent reinforcement learning'"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "返回结果数量，默认5篇"
                    }
                },
                "required": ["query"]
            }
        }
    },
]

# 工具函数映射表
tool_functions = {
    "search": search,
    "get_current_time": get_current_time,
    "calculator": calculator,
    "write_to_file": write_to_file,
    "read_file": read_file,
    "fetch_webpage": fetch_webpage,      # ✅ 新增
    "execute_python": execute_python,
    "search_papers": search_papers      # ✅ 新增
}

# 工具执行日志前缀
tool_emojis = {
    "search": "🔍 搜索",
    "get_current_time": "🕐 获取时间",
    "calculator": "🧮 计算",
    "write_to_file": "📝 保存文件",
    "read_file": "📖 读取文件",
    "fetch_webpage": "🌐 抓取网页",      # ✅ 新增
    "execute_python": "⚡ 执行代码"      # ✅ 新增
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
6. fetch_webpage - 抓取指定网页内容
7. execute_python - 执行Python代码
8. search_papers - 在arXiv上搜索学术论文

请根据用户的问题，选择合适的工具来帮助回答。如果不需要工具，可以直接回答。
调用工具后，请基于工具返回的结果来回答用户。"""}
]
    
    print("🤖 AI Agent 已启动（支持多轮对话，输入 'exit' 退出）")
    print("📋 可用工具：搜索 🔍 | 时间 🕐 | 计算 🧮 | 保存 📝 | 读取 📖 | 抓取网页 🌐 | 执行代码 ⚡ | 论文搜索 📚")
    while True:
        user_input = input("👤 你: ")
        if user_input.lower() in ['exit', 'quit', '退出']:
            print("👋 再见！")
            break
        
        messages.append({"role": "user", "content": user_input})

        # ✅ 在每次对话前，先压缩历史（如果过长）
        messages = compress_conversation(messages)

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
                    elif function_name == "fetch_webpage":
                        result = func(args["url"])
                        print(f"[🌐 抓取网页] {args['url']}")
                    elif function_name == "execute_python":
                        result = func(args["code"], args.get("timeout_seconds", 10))
                        print(f"[⚡ 执行代码] 代码长度: {len(args['code'])} 字符")
                    elif function_name == "search_papers":
                        query = args.get("query", "")
                        max_results = args.get("max_results", 5)
                        result = search_papers(query, max_results)
                        print(f"[📚 论文搜索] 关键词: {query}")    
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