'''
Date         : 2026-08-15 18:50:14
LastEditTime : 2026-08-15 18:50:15
'''
def calculator(expression: str) -> str:
    """执行数学计算"""
    try:
        allowed_chars = set("0123456789+-*/().% **")
        if not all(c in allowed_chars or c.isspace() for c in expression):
            return "❌ 表达式包含不支持的字符"
        result = eval(expression, {"__builtins__": {}}, {})
        return f"计算结果：{expression} = {result}"
    except ZeroDivisionError:
        return "❌ 错误：除数不能为零"
    except Exception as e:
        return f"❌ 计算错误：{str(e)}"