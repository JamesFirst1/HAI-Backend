import os
import uuid
import secrets
import hashlib
from datetime import datetime
from typing import Optional, List
import re

def generate_message_id(prefix: str = "msg") -> str:
    """生成消息ID"""
    timestamp = int(datetime.now().timestamp() * 1000)
    random_part = secrets.token_hex(4)
    return f"{prefix}-{timestamp}-{random_part}"

def generate_ai_message_id() -> str:
    """生成AI消息ID"""
    return generate_message_id("ai")

def generate_memory_id() -> str:
    """生成记忆ID"""
    return f"mem-{uuid.uuid4().hex[:8]}"

def format_timestamp(timestamp: Optional[datetime] = None) -> int:
    """格式化时间戳为整数秒"""
    if timestamp is None:
        timestamp = datetime.now()
    return int(timestamp.timestamp())

def extract_labels_from_text(text: str) -> List[str]:
    """
    从文本中提取关键词作为标签
    这是一个简化版本，实际可以使用NLP库进行关键词提取
    """
    # 移除标点符号
    text_clean = re.sub(r'[^\w\s]', ' ', text.lower())
    
    # 停用词列表
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to',
        'for', 'of', 'with', 'by', 'as', 'is', 'are', 'was', 'were',
        'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
        'will', 'would', 'should', 'could', 'can', 'may', 'might', 'must'
    }
    
    # 分割单词并过滤
    words = text_clean.split()
    keywords = [word for word in words if len(word) > 3 and word not in stop_words]
    
    # 去重并限制数量
    unique_keywords = list(set(keywords))[:10]
    
    return unique_keywords

def validate_image_url(url: str) -> bool:
    """验证图片URL格式"""
    # 简单的URL验证
    url_pattern = re.compile(
        r'^(?:http|https)://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return re.match(url_pattern, url) is not None

def truncate_text(text: str, max_length: int = 200) -> str:
    """截断文本到指定长度，添加省略号"""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."

def generate_password_reset_token() -> str:
    """生成密码重置令牌"""
    return secrets.token_urlsafe(32)

def validate_username(username: str) -> bool:
    """验证用户名格式"""
    # 只允许字母、数字、下划线，长度3-20
    pattern = r'^[a-zA-Z0-9_]{3,20}$'
    return bool(re.match(pattern, username))

def sanitize_filename(filename: str) -> str:
    """清理文件名，移除不安全字符"""
    # 移除路径分隔符和其他不安全字符
    filename = os.path.basename(filename)
    # 替换非字母数字字符为下划线
    filename = re.sub(r'[^\w\.-]', '_', filename)
    return filename[:255]  # 限制长度