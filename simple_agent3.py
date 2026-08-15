'''
Date         : 2026-08-15 18:42:02
LastEditTime : 2026-08-15 18:47:29
'''
'''
Date         : 2026-08-15
LastEditTime : 2026-08-15
'''
import os
import json
import serpapi
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# 1. OpenAI客户端
openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE")
)

# 2. SerpAPI客户端
serpapi_client = serpapi.Client(api_key=os.getenv("SERPAPI_API_KEY"))

# ========== 工具函数定义 ==========

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


def get_current_time() -> str:
    """获取当前日期和时间"""
    now = datetime.now()
    return f"当前时间：{now.strftime('%Y年%m月%d日 %H:%M:%S')} 星期{['一','二','三','四','五','六','日'][now.weekday()]}"


def calculator(expression: str) -> str:
    """执行数学计算，支持 + - * / ** 等运算符"""
    try:
        # 只允许安全的字符，防止恶意代码注入
        allowed_chars = set("0123456789+-*/().% **")
        if not all(c in allowed_chars or c.isspace() for c in expression):
            return "❌ 表达式包含不支持的字符，请使用数字和 + - * / ( ) . ** 运算符"
        
        # 使用eval但限制全局和局部变量为空，只允许数学运算
        result = eval(expression, {"__builtins__": {}}, {})
        return f"计算结果：{expression} = {result}"
    except ZeroDivisionError:
        return "❌ 错误：除数不能为零"
    except Exception as e:
        return f"❌ 计算错误：{str(e)}"


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

# ========== 工具列表（所有可用工具） ==========

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
]

# ========== Agent主循环 ==========

def run_agent():
    messages = [
        {"role": "system", "content": """你是一个智能助理，拥有以下能力：
1. search - 联网搜索实时信息
2. get_current_time - 获取当前时间
3. calculator - 执行数学计算
4. write_to_file - 保存内容到文件

请根据用户的问题，选择合适的工具来帮助回答。如果不需要工具，可以直接回答。
调用工具后，请基于工具返回的结果来回答用户。"""}
    ]
    
    print("🤖 AI Agent 已启动（支持多轮对话，输入 'exit' 退出）")
    print("📋 可用工具：搜索 🔍 | 时间 🕐 | 计算 🧮 | 保存 📝\n")
    
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
                
                # 根据工具名称执行对应的函数
                if function_name == "search":
                    result = search(args["query"])
                    print(f"[🔍 搜索] 关键词: {args['query']}")
                elif function_name == "get_current_time":
                    result = get_current_time()
                    print("[🕐 获取时间]")
                elif function_name == "calculator":
                    result = calculator(args["expression"])
                    print(f"[🧮 计算] {args['expression']}")
                elif function_name == "write_to_file":
                    content = args.get("content", "")
                    filename = args.get("filename", "agent_notes.txt")
                    result = write_to_file(content, filename)
                    print(f"[📝 保存文件] {filename}")
                elif function_name == "read_file":
                    filename = args.get("filename", "agent_notes.txt")
                    result = read_file(filename)
                    print(f"[📖 读取文件] {filename}")
                else:
                    result = f"未知工具: {function_name}"
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })
            
            # 基于工具结果生成最终回答
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