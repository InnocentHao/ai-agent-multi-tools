'''
Date         : 2026-08-16 13:59:07
LastEditTime : 2026-08-16 13:59:40
'''
import subprocess
import tempfile
import os

def execute_python(code: str, timeout_seconds: int = 10) -> str:
    """
    在隔离环境中执行Python代码，返回执行结果或错误信息
    """
    try:
        # 在临时目录中创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(code)
            temp_file = f.name
        
        # 超时控制
        timeout = timeout_seconds if timeout_seconds else 10
        
        # 执行代码
        result = subprocess.run(
            ['python', temp_file],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=tempfile.gettempdir()
        )
        
        # 清理临时文件
        os.unlink(temp_file)
        
        output = ""
        if result.stdout:
            output += f"执行结果：\n{result.stdout.strip()}"
        if result.stderr:
            if output:
                output += "\n\n错误输出：\n"
            else:
                output += "执行出错：\n"
            output += result.stderr.strip()
        
        if not output:
            output = "执行成功，无输出"
        
        return output[:5000]  # 限制输出长度
    
    except subprocess.TimeoutExpired:
        return f"❌ 执行超时（{timeout_seconds}秒），代码可能陷入死循环"
    except Exception as e:
        return f"❌ 执行失败：{str(e)}"