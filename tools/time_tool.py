'''
Date         : 2026-08-15 18:50:06
LastEditTime : 2026-08-15 18:50:07
'''
from datetime import datetime

def get_current_time() -> str:
    """获取当前的日期和时间"""
    now = datetime.now()
    weekdays = ['一', '二', '三', '四', '五', '六', '日']
    return f"当前时间：{now.strftime('%Y年%m月%d日 %H:%M:%S')} 星期{weekdays[now.weekday()]}"